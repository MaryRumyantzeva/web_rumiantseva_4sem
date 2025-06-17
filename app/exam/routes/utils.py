# utils.py
from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Требуется авторизация', 'danger')
                return redirect(url_for('auth.login'))
            if current_user.role.name not in roles:
                flash('Недостаточно прав', 'warning')
                return abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator