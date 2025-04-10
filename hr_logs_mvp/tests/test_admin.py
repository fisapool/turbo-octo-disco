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
def admin_user(app):
    with app.app_context():
        admin = User(
            username='admin',
            email='admin@example.com',
            role=Role.ADMIN
        )
        admin.password = 'admin123'
        db.session.add(admin)
        db.session.commit()
        return admin

@pytest.fixture
def regular_user(app):
    with app.app_context():
        user = User(
            username='regular',
            email='regular@example.com',
            role=Role.EMPLOYEE
        )
        user.password = 'password123'
        db.session.add(user)
        db.session.commit()
        return user

def test_admin_statistics(client, admin_user, regular_user):
    # Login as admin
    client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    
    response = client.get('/api/admin/statistics')
    assert response.status_code == 200
    data = response.get_json()
    assert 'total_users' in data
    assert 'active_logs' in data
    assert 'pending_approvals' in data
    assert 'system_health' in data

def test_admin_user_management(client, admin_user, regular_user):
    # Login as admin
    client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    
    # Get all users
    response = client.get('/api/admin/users')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 2  # At least admin and regular user
    
    # Update user
    response = client.put(f'/api/admin/users/{regular_user.id}', json={
        'username': 'updateduser',
        'email': 'updated@example.com',
        'role': Role.EMPLOYEE
    })
    assert response.status_code == 200
    
    # Delete user
    response = client.delete(f'/api/admin/users/{regular_user.id}')
    assert response.status_code == 200
    assert User.query.get(regular_user.id) is None

def test_admin_log_management(client, admin_user, regular_user):
    # Login as regular user and create a log
    client.post('/login', data={
        'username': 'regular',
        'password': 'password123'
    })
    client.post('/api/logs', json={
        'log_type': 'attendance',
        'description': 'Test log entry'
    })
    
    # Login as admin
    client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    
    # Get all logs
    response = client.get('/api/admin/logs')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0
    
    # Update log status
    log = HRLog.query.filter_by(user_id=regular_user.id).first()
    response = client.put(f'/api/admin/logs/{log.id}', json={
        'status': 'approved',
        'admin_notes': 'Approved by admin'
    })
    assert response.status_code == 200
    updated_log = HRLog.query.get(log.id)
    assert updated_log.status == 'approved'
    assert updated_log.admin_notes == 'Approved by admin' 