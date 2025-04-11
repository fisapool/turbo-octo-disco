from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from models import User, Role, Log, Department, HRLog
from .. import db
from .roles import admin_required
import psutil
import os

api = Blueprint('api', __name__)

@api.route('/logs', methods=['GET'])
@login_required
def get_logs():
    """Get all logs for the current user or all logs if admin"""
    if current_user.role == Role.ADMIN:
        logs = HRLog.query.order_by(HRLog.timestamp.desc()).all()
    else:
        logs = HRLog.query.filter_by(user_id=current_user.id).order_by(HRLog.timestamp.desc()).all()
    return jsonify([log.to_dict() for log in logs])

@api.route('/logs', methods=['POST'])
@login_required
def create_log():
    """Create a new HR log"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('log_type', 'description')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    new_log = HRLog(
        user_id=current_user.id,
        log_type=data['log_type'],
        description=data['description'],
        status='pending',
        timestamp=datetime.utcnow()
    )
    
    db.session.add(new_log)
    db.session.commit()
    
    return jsonify(new_log.to_dict()), 201

@api.route('/logs/<int:log_id>', methods=['PUT'])
@login_required
def update_log(log_id):
    """Update an existing HR log"""
    log = HRLog.query.get_or_404(log_id)
    
    if log.user_id != current_user.id and current_user.role != Role.ADMIN:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'status' in data:
        if current_user.role != Role.ADMIN:
            return jsonify({'error': 'Only admins can change status'}), 403
        log.status = data['status']
    if 'description' in data:
        log.description = data['description']
    
    db.session.commit()
    return jsonify(log.to_dict())

@api.route('/logs/<int:log_id>', methods=['DELETE'])
@login_required
def delete_log(log_id):
    """Delete an HR log"""
    log = HRLog.query.get_or_404(log_id)
    
    if log.user_id != current_user.id and current_user.role != Role.ADMIN:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(log)
    db.session.commit()
    return jsonify({'message': 'Log deleted successfully'})

@api.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users (admin only)"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@api.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update user details (admin only)"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'role' in data:
        user.role = data['role']
    if 'email' in data:
        user.email = data['email']
    
    db.session.commit()
    return jsonify(user.to_dict())

@api.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    # Check system resources
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'cpu_usage': cpu_percent,
        'memory_usage': memory_percent,
        'timestamp': datetime.utcnow().isoformat()
    })

@api.route('/admin/statistics')
@login_required
@admin_required
def get_statistics():
    total_users = User.query.count()
    active_logs = HRLog.query.filter_by(status='active').count()
    pending_approvals = HRLog.query.filter_by(status='pending').count()
    
    # Calculate system health (simplified example)
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    system_health = 100 - ((cpu_percent + memory_percent) / 2)
    
    return jsonify({
        'total_users': total_users,
        'active_logs': active_logs,
        'pending_approvals': pending_approvals,
        'system_health': round(system_health, 2)
    })

@api.route('/admin/users')
@login_required
@admin_required
def get_admin_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'last_login': user.last_login.isoformat() if user.last_login else None
    } for user in users])

@api.route('/admin/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
@admin_required
def manage_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        })
    
    elif request.method == 'PUT':
        data = request.get_json()
        user.username = data['username']
        user.email = data['email']
        user.role = data['role']
        db.session.commit()
        return jsonify({'message': 'User updated successfully'})
    
    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})

@api.route('/admin/logs')
@login_required
@admin_required
def get_admin_logs():
    logs = HRLog.query.join(User).add_columns(
        HRLog.id,
        User.username,
        HRLog.log_type,
        HRLog.description,
        HRLog.status,
        HRLog.timestamp,
        HRLog.admin_notes
    ).all()
    
    return jsonify([{
        'id': log.id,
        'username': log.username,
        'log_type': log.log_type,
        'description': log.description,
        'status': log.status,
        'timestamp': log.timestamp.isoformat(),
        'admin_notes': log.admin_notes
    } for log in logs])

@api.route('/admin/logs/<int:log_id>', methods=['GET', 'PUT'])
@login_required
@admin_required
def manage_admin_log(log_id):
    log = HRLog.query.get_or_404(log_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': log.id,
            'status': log.status,
            'admin_notes': log.admin_notes
        })
    
    elif request.method == 'PUT':
        data = request.get_json()
        log.status = data['status']
        log.admin_notes = data['admin_notes']
        db.session.commit()
        return jsonify({'message': 'Log updated successfully'})

@api.route('/admin/system-health')
@login_required
@admin_required
def get_system_health():
    # Database status (simplified example)
    try:
        db.session.execute('SELECT 1')
        db_status = 100
    except:
        db_status = 0
    
    # System resources
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    system_resources = 100 - ((cpu_percent + memory_percent) / 2)
    
    return jsonify({
        'db_status': db_status,
        'system_resources': round(system_resources, 2)
    }) 