from functools import wraps
from flask import abort
from flask_login import current_user

class Role:
    ADMIN = 'admin'
    EMPLOYEE = 'employee'

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return role_required(Role.ADMIN)(f)

def employee_required(f):
    return role_required(Role.EMPLOYEE)(f) 