"""Session-key persistence, deletion CSRF, and safe post-login destinations."""

import re

import pytest
from flask import Flask
from flask.sessions import SecureCookieSessionInterface
from flask.testing import FlaskClient

from app import create_app, db
from app.models import Property, Stand, User
from app.security import load_secret_key


@pytest.fixture
def client(app):
    # The shared DB fixture holds an outer app context open. Give each HTTP request
    # its own context, as in the running app, so Flask-Login and CSRF values in g
    # cannot leak between different requests or different test clients.
    class RequestContextClient(FlaskClient):
        def open(self, *args, **kwargs):
            with self.application.app_context():
                return super().open(*args, **kwargs)

    app.test_client_class = RequestContextClient
    return app.test_client()


def csrf_token(response):
    match = re.search(rb'name="csrf_token"[^>]*value="([^"]+)"', response.data)
    assert match is not None
    return match.group(1).decode('ascii')


@pytest.fixture
def security_data(client):
    owner = User(username='security_owner')
    owner.set_password('security-password')
    other = User(username='security_other')
    other.set_password('other-password')
    prop = Property(name='Owned Property', owner=owner)
    foreign = Property(name='Other Property', owner=other)
    stand = Stand(name='Owned Stand', degree=90, property=prop)
    foreign_stand = Stand(name='Other Stand', degree=180, property=foreign)
    db.session.add_all([owner, other, prop, foreign, stand, foreign_stand])
    db.session.commit()
    identifiers = {
        'owner': owner.id, 'property': prop.id, 'stand': stand.id,
        'other': other.id, 'foreign': foreign.id, 'foreign_stand': foreign_stand.id,
    }
    client.post('/login', data={'username': 'security_owner', 'password': 'security-password'})
    return identifiers


def test_default_secret_is_random_persisted_and_unique_per_instance(tmp_path, monkeypatch):
    monkeypatch.delenv('SECRET_KEY', raising=False)
    first = create_app(instance_path=str(tmp_path / 'first'))
    restarted = create_app(instance_path=str(tmp_path / 'first'))
    separate = create_app(instance_path=str(tmp_path / 'second'))
    assert len(first.secret_key) == 64
    assert first.secret_key != 'some-secret-key'
    assert first.secret_key == restarted.secret_key
    assert first.secret_key != separate.secret_key
    assert (tmp_path / 'first' / 'secret_key').read_text() == first.secret_key


def test_environment_secret_overrides_local_key_without_replacing_it(tmp_path, monkeypatch):
    monkeypatch.delenv('SECRET_KEY', raising=False)
    local = load_secret_key(tmp_path)
    monkeypatch.setenv('SECRET_KEY', 'test-environment-key-' + 'a' * 48)
    configured = create_app(instance_path=str(tmp_path))
    assert configured.secret_key == 'test-environment-key-' + 'a' * 48
    assert (tmp_path / 'secret_key').read_text() == local
    monkeypatch.delenv('SECRET_KEY')
    assert load_secret_key(tmp_path) == local


def test_explicit_test_configuration_does_not_generate_local_secret(tmp_path):
    app = create_app({
        'TESTING': True, 'SECRET_KEY': 'isolated-test-key',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    }, instance_path=str(tmp_path))
    assert app.secret_key == 'isolated-test-key'
    assert not (tmp_path / 'secret_key').exists()


def test_short_configured_secret_fails_clearly(tmp_path, monkeypatch):
    monkeypatch.setenv('SECRET_KEY', 'some-secret-key')
    with pytest.raises(RuntimeError, match='at least 32'):
        load_secret_key(tmp_path)


def test_invalid_local_secret_is_not_silently_replaced(tmp_path, monkeypatch):
    monkeypatch.delenv('SECRET_KEY', raising=False)
    key_path = tmp_path / 'secret_key'
    key_path.write_text('')
    with pytest.raises(RuntimeError, match='local instance/secret_key is invalid'):
        load_secret_key(tmp_path)
    assert key_path.read_text() == ''


def test_cookie_signed_with_old_hardcoded_key_is_rejected(client, app, security_data, tmp_path, monkeypatch):
    monkeypatch.delenv('SECRET_KEY', raising=False)
    app.secret_key = load_secret_key(tmp_path)
    legacy = Flask('legacy-cookie')
    legacy.secret_key = 'some-secret-key'
    signer = SecureCookieSessionInterface().get_signing_serializer(legacy)
    forged = signer.dumps({'_user_id': str(security_data['owner']), '_fresh': True})
    client.set_cookie(app.config['SESSION_COOKIE_NAME'], forged)
    response = client.get('/properties')
    assert response.status_code == 302 and '/login' in response.headers['Location']
    client.post('/login', data={'username': 'security_owner', 'password': 'security-password'})
    assert client.get('/properties').status_code == 200


@pytest.mark.parametrize('kind', ['property', 'account'])
def test_deletion_rejects_missing_and_tampered_csrf(client, app, security_data, kind):
    app.config['WTF_CSRF_ENABLED'] = True
    page = '/properties' if kind == 'property' else '/profile'
    url = f"/property/{security_data['property']}/delete" if kind == 'property' else '/profile/delete'
    token = csrf_token(client.get(page))
    assert client.post(url).status_code == 400
    assert client.post(url, data={'csrf_token': 'tampered-' + token}).status_code == 400
    assert db.session.get(User, security_data['owner']) is not None
    assert db.session.get(Property, security_data['property']) is not None
    assert db.session.get(Stand, security_data['stand']) is not None
    assert client.get('/properties').status_code == 200  # A rejected deletion must not log the user out.


@pytest.mark.parametrize('kind', ['property', 'account'])
def test_deletion_rejects_token_from_another_session(client, app, security_data, kind):
    app.config['WTF_CSRF_ENABLED'] = True
    csrf_token(client.get('/profile'))  # Establish this session's own CSRF value.
    other = app.test_client()
    login_token = csrf_token(other.get('/login'))
    other.post('/login', data={
        'username': 'security_other', 'password': 'other-password', 'csrf_token': login_token,
    })
    other_token = csrf_token(other.get('/profile'))
    url = f"/property/{security_data['property']}/delete" if kind == 'property' else '/profile/delete'
    assert client.post(url, data={'csrf_token': other_token}).status_code == 400
    assert db.session.get(User, security_data['owner']) is not None
    assert db.session.get(Stand, security_data['stand']) is not None


@pytest.mark.parametrize('kind', ['property', 'account'])
def test_valid_deletion_preserves_other_users_and_cascades_owned_data(client, app, security_data, kind):
    app.config['WTF_CSRF_ENABLED'] = True
    page = '/properties' if kind == 'property' else '/profile'
    url = f"/property/{security_data['property']}/delete" if kind == 'property' else '/profile/delete'
    token = csrf_token(client.get(page))
    assert client.post(url, data={'csrf_token': token}).status_code == 302
    db.session.expire_all()
    assert db.session.get(Property, security_data['property']) is None
    assert db.session.get(Stand, security_data['stand']) is None
    assert (db.session.get(User, security_data['owner']) is None) == (kind == 'account')
    assert db.session.get(User, security_data['other']) is not None
    assert db.session.get(Property, security_data['foreign']) is not None
    assert db.session.get(Stand, security_data['foreign_stand']) is not None
    if kind == 'account':
        assert '/login' in client.get('/properties').headers['Location']


def test_property_ownership_still_checked_with_valid_csrf(client, app, security_data):
    app.config['WTF_CSRF_ENABLED'] = True
    token = csrf_token(client.get('/properties'))
    response = client.post(f"/property/{security_data['foreign']}/delete", data={'csrf_token': token})
    assert response.status_code == 403
    assert db.session.get(Property, security_data['foreign']) is not None


@pytest.mark.parametrize('target', [
    '/properties', '/profile', '/properties?sort=name#top',
    '/properties?name=New%20Property', '/%70roperties',
])
def test_login_preserves_safe_local_return_paths(client, security_data, target):
    client.get('/logout')
    response = client.post('/login', query_string={'next': target}, data={
        'username': 'security_owner', 'password': 'security-password',
    })
    assert response.status_code == 302
    assert response.headers['Location'] == target
    assert client.get('/properties').status_code == 200


@pytest.mark.parametrize('target', [
    'https://attacker.example', 'http://localhost/properties', '//attacker.example',
    '///attacker.example', r'/\attacker.example', r'\\attacker.example',
    'javascript:alert(1)', 'data:text/html,hello', ' https://attacker.example',
    '\t//attacker.example', '/\n/attacker.example', '/%09/attacker.example',
    '/%2f%2fattacker.example', '/%252f%252fattacker.example',
    '/%5cattacker.example', '/%255cattacker.example', '/%ff', '',
])
def test_login_ignores_unsafe_return_paths(client, security_data, target):
    client.get('/logout')
    response = client.post('/login', query_string={'next': target}, data={
        'username': 'security_owner', 'password': 'security-password',
    })
    assert response.status_code == 302
    assert response.headers['Location'] == '/'
    assert client.get('/properties').status_code == 200
