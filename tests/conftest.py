import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create the app with common test config
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False, # Disable CSRF for testing forms
    })

    # create the database and load test data
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's click commands."""
    return app.test_cli_runner()

@pytest.fixture
def init_database(app):
    """Fixture to initialize database with some basic data if needed."""
    with app.app_context():
        db.session.commit()
