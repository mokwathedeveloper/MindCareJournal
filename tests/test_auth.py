import pytest
from app import app, db
from models import User
from flask_auth import authenticate_user, register_user

# Setup a test client for the Flask app
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Use in-memory SQLite for testing
    app.secret_key = 'test_secret_key' # Set a dummy secret key for testing
    app.config['MAIL_SERVER'] = 'localhost' # Dummy mail server for testing
    app.config['MAIL_PORT'] = 25 # Dummy mail port for testing
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'test@example.com'
    app.config['MAIL_PASSWORD'] = 'password'
    app.config['MAIL_DEFAULT_SENDER'] = 'test@example.com'
    app.config['DATABASE_URL'] = 'sqlite:///:memory:' # Dummy DATABASE_URL for testing

    with app.test_client() as client:
        with app.app_context():
            db.create_all() # Create tables for testing
        yield client
        with app.app_context():
            db.drop_all() # Clean up after tests

# Test user registration
def test_register_user_success(client):
    with app.app_context():
        user = register_user("testuser", "test@example.com", "password123")
        assert user is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert User.query.filter_by(username="testuser").first() is not None

def test_register_user_duplicate_username(client):
    with app.app_context():
        register_user("testuser", "test@example.com", "password123")
        user = register_user("testuser", "another@example.com", "password123")
        assert user is None # Should fail due to duplicate username

def test_register_user_duplicate_email(client):
    with app.app_context():
        register_user("testuser", "test@example.com", "password123")
        user = register_user("anotheruser", "test@example.com", "password123")
        assert user is None # Should fail due to duplicate email

# Test user authentication
def test_authenticate_user_success(client):
    with app.app_context():
        register_user("authuser", "auth@example.com", "authpassword")
        user = authenticate_user("authuser", "authpassword")
        assert user is not None
        assert user.username == "authuser"

def test_authenticate_user_incorrect_password(client):
    with app.app_context():
        register_user("authuser", "auth@example.com", "authpassword")
        user = authenticate_user("authuser", "wrongpassword")
        assert user is None

def test_authenticate_user_non_existent_user(client):
    with app.app_context():
        user = authenticate_user("nonexistent", "password")
        assert user is None

def test_authenticate_user_deactivated_user(client):
    with app.app_context():
        user = register_user("deactivated", "deactivated@example.com", "password123")
        user.is_active = False
        db.session.commit()
        
        authenticated_user = authenticate_user("deactivated", "password123")
        assert authenticated_user is None
