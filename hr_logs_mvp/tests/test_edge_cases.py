import pytest
from app import create_app
from app.models import User, HRLog, db
from app.roles import Role
from datetime import datetime
from werkzeug.exceptions import HTTPException

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

# Authentication Edge Cases
def test_register_duplicate_username(client):
    # First registration
    client.post('/register', data={
        'username': 'testuser',
        'email': 'test1@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    
    # Try to register with same username
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'test2@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    assert b'Username already exists' in response.data

def test_register_duplicate_email(client):
    # First registration
    client.post('/register', data={
        'username': 'user1',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    
    # Try to register with same email
    response = client.post('/register', data={
        'username': 'user2',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    assert b'Email already exists' in response.data

def test_register_invalid_email(client):
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'invalid-email',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    assert b'Invalid email address' in response.data

def test_register_password_mismatch(client):
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'differentpassword'
    })
    assert b'Passwords do not match' in response.data

# Log Management Edge Cases
def test_create_log_invalid_type(client, logged_in_user):
    response = client.post('/api/logs', json={
        'log_type': 'invalid_type',
        'description': 'Test log'
    })
    assert response.status_code == 400

def test_create_log_missing_fields(client, logged_in_user):
    response = client.post('/api/logs', json={
        'log_type': 'attendance'
        # Missing description
    })
    assert response.status_code == 400

def test_update_nonexistent_log(client, logged_in_user):
    response = client.put('/api/logs/999999', json={
        'description': 'Updated description'
    })
    assert response.status_code == 404

def test_delete_nonexistent_log(client, logged_in_user):
    response = client.delete('/api/logs/999999')
    assert response.status_code == 404

# Admin Edge Cases
def test_admin_access_unauthorized(client, logged_in_user):
    response = client.get('/api/admin/statistics')
    assert response.status_code == 403

def test_admin_update_nonexistent_user(client, logged_in_user):
    # Create admin user
    admin = User(
        username='admin',
        email='admin@example.com',
        role=Role.ADMIN
    )
    admin.password = 'admin123'
    db.session.add(admin)
    db.session.commit()
    
    # Login as admin
    client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    
    response = client.put('/api/admin/users/999999', json={
        'username': 'updated',
        'email': 'updated@example.com',
        'role': Role.EMPLOYEE
    })
    assert response.status_code == 404

def test_admin_delete_nonexistent_user(client, logged_in_user):
    # Create admin user
    admin = User(
        username='admin',
        email='admin@example.com',
        role=Role.ADMIN
    )
    admin.password = 'admin123'
    db.session.add(admin)
    db.session.commit()
    
    # Login as admin
    client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    
    response = client.delete('/api/admin/users/999999')
    assert response.status_code == 404

# Database Error Handling
def test_database_connection_error(app, client):
    # Simulate database connection error
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nonexistent/path/database.db'
    
    with pytest.raises(Exception):
        client.get('/')

# Rate Limiting (simulated)
def test_rate_limiting(client, logged_in_user):
    # Simulate multiple rapid requests
    for _ in range(11):  # Assuming rate limit is 10 requests per minute
        response = client.get('/api/logs')
    
    assert response.status_code == 429  # Too Many Requests

# Input Validation
def test_xss_attempt(client, logged_in_user):
    xss_payload = '<script>alert("XSS")</script>'
    response = client.post('/api/logs', json={
        'log_type': 'attendance',
        'description': xss_payload
    })
    assert response.status_code == 400  # Should sanitize input

def test_sql_injection_attempt(client, logged_in_user):
    sql_payload = "'; DROP TABLE users; --"
    response = client.post('/api/logs', json={
        'log_type': 'attendance',
        'description': sql_payload
    })
    assert response.status_code == 400  # Should prevent SQL injection 