from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            flash('Access denied! Admin only.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def hr_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        allowed_roles = ['Admin', 'HR Manager']
        if not current_user.role or current_user.role.name not in allowed_roles:
            flash('Access denied! HR Manager or Admin only.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function