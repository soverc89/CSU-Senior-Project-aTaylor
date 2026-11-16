"""Map locations, ownership, coordinate validation, and legacy database upgrades."""

import json
import re
from unittest.mock import patch

import pytest
from sqlalchemy import inspect, text

from app import db
from app.models import Property, Stand, User
from app.schema import upgrade_stand_locations


@pytest.fixture
def map_property(client):
    owner = User(username='map_owner')
    owner.set_password('map_password')
    other = User(username='other_owner')
    other.set_password('other_password')
    prop = Property(name='Map Test Property', latitude=34.0, longitude=-81.0, owner=owner)
    second = Property(name='Second Property', owner=owner)
    foreign = Property(name='Private Property', owner=other)
    db.session.add_all([owner, other, prop, second, foreign])
    db.session.commit()
    client.post('/login', data={'username': 'map_owner', 'password': 'map_password'})
    return prop


def payload(response):
    match = re.search(rb'<script id="map-data" type="application/json">(.*?)</script>', response.data, re.S)
    assert match is not None
    return json.loads(match.group(1))


def test_map_click_prefills_form_without_creating_stand(client, map_property):
    response = client.get(f'/property/{map_property.id}/stand/new?latitude=34.001234&longitude=-81.002345')
    assert response.status_code == 200
    assert b'value="34.001234"' in response.data
    assert b'value="-81.002345"' in response.data
    assert Stand.query.count() == 0


def test_stand_form_offers_device_location_and_saves_it_without_moving_property(client, map_property):
    url = f'/property/{map_property.id}/stand/new'
    response = client.get(url)
    assert response.status_code == 200
    assert b'id="find-stand-location"' in response.data
    assert b'Find My Location' in response.data and b'/static/stand-location.js' in response.data
    assert Stand.query.count() == 0
    response = client.post(url, data={
        'name': 'Field Stand', 'degree': '0', 'latitude': '34.001234', 'longitude': '-81.002345',
    })
    assert response.status_code == 302
    stand = Stand.query.one()
    assert (stand.latitude, stand.longitude) == (34.001234, -81.002345)
    db.session.refresh(map_property)
    assert (map_property.latitude, map_property.longitude) == (34, -81)
    editor = client.get(f'/property/{map_property.id}/stand/{stand.id}/edit')
    assert b'id="find-stand-location"' in editor.data


def test_direction_dial_is_available_on_creation_and_editing_and_heading_saves(client, map_property):
    url = f'/property/{map_property.id}/stand/new'
    creation = client.get(url)
    assert b'id="stand-direction-dial"' in creation.data
    assert b'role="slider"' in creation.data and b'/static/stand-direction.js' in creation.data
    assert Stand.query.count() == 0
    saved = client.post(url, data={'name': 'Aimed Stand', 'degree': '135'})
    assert saved.status_code == 302
    stand = Stand.query.one()
    assert stand.degree == 135
    editing = client.get(f'/property/{map_property.id}/stand/{stand.id}/edit')
    assert b'id="stand-direction-dial"' in editing.data
    assert b'value="135"' in editing.data


@pytest.mark.parametrize('latitude, longitude', [('nan', '-81'), ('34', 'inf'), ('91', '-81'), ('34', '-181'), ('34', '')])
def test_invalid_map_link_does_not_prefill_location(client, map_property, latitude, longitude):
    response = client.get(f'/property/{map_property.id}/stand/new?latitude={latitude}&longitude={longitude}')
    assert response.status_code == 200
    assert b'That map location is invalid' in response.data
    assert Stand.query.count() == 0


@pytest.mark.parametrize('degree', [0, 360])
def test_save_map_location_and_valid_heading_endpoints(client, map_property, degree):
    response = client.post(f'/property/{map_property.id}/stand/new', data={
        'name': 'Mapped Stand', 'degree': str(degree), 'latitude': '0', 'longitude': '0',
    })
    assert response.status_code == 302
    stand = Stand.query.one()
    assert (stand.latitude, stand.longitude, stand.degree) == (0, 0, degree)
    with patch('app.weather.WeatherManager.get_wind_direction', return_value=180) as weather:
        dashboard = client.get(f'/property/{map_property.id}/stands')
    weather.assert_called_once_with(34.0, -81.0)
    marker = payload(dashboard)['stands'][0]
    assert (marker['latitude'], marker['longitude'], marker['score']) == (0, 0, 100)


@pytest.mark.parametrize('changes', [
    {'latitude': '91'}, {'longitude': '-181'}, {'latitude': 'nan'},
    {'longitude': 'inf'}, {'latitude': 'text'}, {'longitude': ''},
    {'latitude': ''}, {'degree': '-1'}, {'degree': '361'},
    {'degree': 'text'}, {'degree': '90.5'},
])
def test_reject_invalid_stand_form_without_saving(client, map_property, changes):
    data = {'name': 'Invalid Stand', 'degree': '0', 'latitude': '34', 'longitude': '-81'}
    data.update(changes)
    response = client.post(f'/property/{map_property.id}/stand/new', data=data)
    assert response.status_code == 200
    assert Stand.query.count() == 0


def test_edit_and_clear_location(client, map_property):
    stand = Stand(name='Existing Stand', degree=90, property=map_property, latitude=34, longitude=-81)
    db.session.add(stand)
    db.session.commit()
    url = f'/property/{map_property.id}/stand/{stand.id}/edit'
    response = client.post(url, data={'name': 'Moved Stand', 'degree': '180', 'latitude': '34.01', 'longitude': '-81.02'})
    assert response.status_code == 302
    db.session.refresh(stand)
    assert (stand.name, stand.latitude, stand.longitude, stand.degree) == ('Moved Stand', 34.01, -81.02, 180)
    response = client.post(url, data={'name': 'Moved Stand', 'degree': '180', 'latitude': '', 'longitude': ''})
    assert response.status_code == 302
    db.session.refresh(stand)
    assert stand.latitude is None and stand.longitude is None


def test_dashboard_legacy_stands_and_safe_marker_names(client, map_property):
    name = '</script><script>alert(1)</script>'
    db.session.add_all([
        Stand(name=name, degree=0, property=map_property, latitude=34.01, longitude=-81.01),
        Stand(name='Unplaced Legacy Stand', degree=None, property=map_property),
    ])
    db.session.commit()
    with patch('app.weather.WeatherManager.get_wind_direction', return_value=180):
        response = client.get(f'/property/{map_property.id}/stands')
    assert response.status_code == 200
    data = payload(response)
    assert len(data['stands']) == 1
    assert data['stands'][0]['name'] == name
    assert name.encode() not in response.data
    assert b'Unplaced Legacy Stand' in response.data and b'Place on map' in response.data


def test_map_without_property_coordinates_or_weather(client, map_property):
    map_property.latitude = map_property.longitude = None
    db.session.add(Stand(name='Located Stand', degree=0, property=map_property, latitude=34.01, longitude=-81.01))
    db.session.commit()
    with patch('app.weather.WeatherManager.get_wind_direction', return_value=None):
        response = client.get(f'/property/{map_property.id}/stands')
    assert response.status_code == 200
    data = payload(response)
    assert data['property']['latitude'] is None
    assert data['stands'][0]['score'] is None
    assert b"Set the property's coordinates" in response.data


def test_map_routes_enforce_property_and_stand_ownership(client, map_property):
    foreign = Property.query.filter_by(name='Private Property').one()
    second = Property.query.filter_by(name='Second Property').one()
    stand = Stand(name='Private Stand', degree=0, property=foreign, latitude=34, longitude=-81)
    db.session.add(stand)
    db.session.commit()
    assert client.get(f'/property/{foreign.id}/stands').status_code == 403
    assert client.get(f'/property/{foreign.id}/stand/new?latitude=34&longitude=-81').status_code == 403
    assert client.post(f'/property/{foreign.id}/stand/new', data={'name': 'Intruder', 'degree': '0'}).status_code == 403
    for method in ('get', 'post'):
        assert getattr(client, method)(f'/property/{second.id}/stand/{stand.id}/edit').status_code == 403
    assert client.post(f'/property/{second.id}/stand/{stand.id}/delete').status_code == 403
    assert client.post(f'/property/{foreign.id}/stand/{stand.id}/delete').status_code == 403
    assert Stand.query.count() == 1


def test_map_delete_requires_csrf_and_removes_marker(client, app, map_property):
    stand = Stand(name='Delete From Map', degree=0, property=map_property, latitude=34, longitude=-81)
    db.session.add(stand)
    db.session.commit()
    app.config['WTF_CSRF_ENABLED'] = True
    url = f'/property/{map_property.id}/stand/{stand.id}/delete'
    assert client.post(url).status_code == 400
    with patch('app.weather.WeatherManager.get_wind_direction', return_value=180):
        dashboard = client.get(f'/property/{map_property.id}/stands')
        token = payload(dashboard)['csrf_token']
        assert token
        assert client.post(url, data={'csrf_token': token}).status_code == 302
        assert payload(client.get(f'/property/{map_property.id}/stands'))['stands'] == []
    assert Stand.query.count() == 0


@pytest.mark.parametrize('coordinates', [
    {'latitude': 'nan', 'longitude': '-81'},
    {'latitude': '34', 'longitude': ''},
    {'latitude': '34', 'longitude': '181'},
])
def test_property_coordinates_are_validated(client, map_property, coordinates):
    response = client.post(f'/property/{map_property.id}/edit', data={'name': map_property.name, **coordinates})
    assert response.status_code == 200
    db.session.refresh(map_property)
    assert (map_property.latitude, map_property.longitude) == (34, -81)


def test_zero_property_coordinate_is_not_lost_on_edit(client, map_property):
    map_property.latitude = map_property.longitude = 0
    db.session.commit()
    response = client.get(f'/property/{map_property.id}/edit')
    assert b'value="0.0"' in response.data
    assert b'0.0, 0.0' in client.get('/properties').data


def test_upgrade_legacy_schema_preserves_data_and_is_repeatable(app):
    with db.engine.begin() as connection:
        connection.execute(text('DROP TABLE stands'))
        connection.execute(text('CREATE TABLE stands (id INTEGER PRIMARY KEY, name VARCHAR(100), degree INTEGER, property_id INTEGER)'))
        connection.execute(text("INSERT INTO stands VALUES (7, 'Legacy Stand', 90, 3)"))
    upgrade_stand_locations()
    with db.engine.begin() as connection:
        assert connection.execute(text('SELECT * FROM stands')).one() == (7, 'Legacy Stand', 90, 3, None, None)
        connection.execute(text('UPDATE stands SET latitude = 34, longitude = -81 WHERE id = 7'))
    upgrade_stand_locations()
    with db.engine.connect() as connection:
        assert connection.execute(text('SELECT latitude, longitude FROM stands WHERE id = 7')).one() == (34, -81)
        assert len(inspect(connection).get_columns('stands')) == 6
