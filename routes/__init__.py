from functools import wraps
from flask import session, flash, redirect, url_for, request
from models import User

def login_required(f):
    """Decorator ensuring that only authenticated users can access the endpoint."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this feature.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator ensuring that only users with role='admin' can access the endpoint."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Administrator login required.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        if session.get('role') != 'admin':
            flash("Access denied: Administrator privileges required.", "danger")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function
