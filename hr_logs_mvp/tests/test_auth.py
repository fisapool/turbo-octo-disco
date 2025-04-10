import pytest
from app import create_app
from app.models import User, db
from app.roles import Role

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_register(client):
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    assert response.status_code == 302  # Redirect after successful registration
    assert User.query.filter_by(username='testuser').first() is not None

def test_login(client):
    # First register a user
    client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    
    # Then test login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 302  # Redirect after successful login

def test_login_invalid_credentials(client):
    response = client.post('/login', data={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    })
    assert b'Invalid username or password' in response.data

def test_logout(client):
    # First login
    client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    
    # Then test logout
    response = client.get('/logout')
    assert response.status_code == 302  # Redirect after logout 