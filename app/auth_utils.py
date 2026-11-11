from functools import wraps
from flask import session, redirect, url_for, flash, request, abort
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    """Hashes a plain-text password using Werkzeug's secure hashing algorithm."""
    return generate_password_hash(password, method='scrypt')

def verify_password(stored_hash: str, password: str) -> bool:
    """Verifies a plain-text password against the stored hash."""
    return check_password_hash(stored_hash, password)

def login_required(f):
    """Decorator to protect routes requiring an authenticated user."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    """Decorator to protect routes requiring Manager privileges.
    Regular Users are strictly denied access.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Manager authentication required.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        if session.get('role') != 'manager':
            flash("Access denied: You need Manager privileges to view this area.", "error")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Returns a dictionary with current session user info or None."""
    if 'user_id' in session:
        return {
            'id': session.get('user_id'),
            'name': session.get('user_name'),
            'email': session.get('user_email'),
            'role': session.get('role')
        }
    return None
