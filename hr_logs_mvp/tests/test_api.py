import pytest
from app import create_app
from app.models import User, HRLog, db
from app.roles import Role
from datetime import datetime

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

@pytest.fixture
def logged_in_user(app, client):
    # Register and login a user
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
    return User.query.filter_by(username='testuser').first()

def test_api_authentication(client):
    # Test protected endpoint without authentication
    response = client.get('/api/logs')
    assert response.status_code == 401

def test_api_log_creation(client, logged_in_user):
    response = client.post('/api/logs', json={
        'log_type': 'attendance',
        'description': 'Test API log'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['log_type'] == 'attendance'
    assert data['description'] == 'Test API log'
    assert data['status'] == 'pending'

def test_api_log_retrieval(client, logged_in_user):
    # Create a log first
    client.post('/api/logs', json={
        'log_type': 'attendance',
        'description': 'Test API log'
    })
    
    response = client.get('/api/logs')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0
    assert data[0]['log_type'] == 'attendance'

def test_api_log_update(client, logged_in_user):
    # Create a log first
    client.post('/api/logs', json={
        'log_type': 'attendance',
        'description': 'Test API log'
    })
    log = HRLog.query.filter_by(user_id=logged_in_user.id).first()
    
    response = client.put(f'/api/logs/{log.id}', json={
        'description': 'Updated via API'
    })
    assert response.status_code == 200
    updated_log = HRLog.query.get(log.id)
    assert updated_log.description == 'Updated via API'

def test_api_log_deletion(client, logged_in_user):
    # Create a log first
    client.post('/api/logs', json={
        'log_type': 'attendance',
        'description': 'Test API log'
    })
    log = HRLog.query.filter_by(user_id=logged_in_user.id).first()
    
    response = client.delete(f'/api/logs/{log.id}')
    assert response.status_code == 200
    assert HRLog.query.get(log.id) is None

def test_api_system_health(client, logged_in_user):
    response = client.get('/api/admin/system-health')
    assert response.status_code == 403  # Regular users can't access admin endpoints
    
    # Create admin user and login
    admin = User(
        username='admin',
        email='admin@example.com',
        role=Role.ADMIN
    )
    admin.password = 'admin123'
    db.session.add(admin)
    db.session.commit()
    
    client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    
    response = client.get('/api/admin/system-health')
    assert response.status_code == 200
    data = response.get_json()
    assert 'db_status' in data
    assert 'system_resources' in data 