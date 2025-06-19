from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(*roles):
    """Декоратор для проверки ролей"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not any(getattr(current_user, 'is_' + role, False) for role in roles):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator