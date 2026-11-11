import re
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.db import get_users_collection, check_db_connection
from app.auth_utils import hash_password, verify_password, get_current_user

auth_bp = Blueprint('auth', __name__)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # If user is already logged in, redirect
    if 'user_id' in session:
        if session.get('role') == 'manager':
            return redirect(url_for('manager.dashboard'))
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        preferred_size = request.form.get('preferred_size', '')

        # Validations
        if not name or not email or not password:
            flash("All required fields must be filled.", "error")
            return render_template('register.html', name=name, email=email, preferred_size=preferred_size)

        if not EMAIL_REGEX.match(email):
            flash("Please enter a valid email address.", "error")
            return render_template('register.html', name=name, email=email, preferred_size=preferred_size)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template('register.html', name=name, email=email, preferred_size=preferred_size)

        if confirm_password and password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template('register.html', name=name, email=email, preferred_size=preferred_size)

        # Check DB connection
        db_ok, db_msg = check_db_connection()
        if not db_ok:
            flash(f"Database error: {db_msg}. Please ensure MongoDB is running.", "error")
            return render_template('register.html', name=name, email=email, preferred_size=preferred_size)

        users_col = get_users_collection()
        if users_col is None:
            flash("Could not access users collection in database.", "error")
            return render_template('register.html', name=name, email=email, preferred_size=preferred_size)

        # Check if email already registered
        existing_user = users_col.find_one({"email": email})
        if existing_user:
            flash("An account with this email address already exists. Please sign in.", "error")
            return render_template('register.html', name=name, email=email, preferred_size=preferred_size)

        # Hash password and create record
        # Note: Normal registration strictly assigns the 'user' role
        pw_hash = hash_password(password)
        new_user = {
            "name": name,
            "email": email,
            "password_hash": pw_hash,
            "role": "user",  # Strict: cannot be manager
            "preferred_size": int(preferred_size) if preferred_size and preferred_size.isdigit() else None,
            "created_at": datetime.now(timezone.utc)
        }

        try:
            result = users_col.insert_one(new_user)
            # Automatically establish user session
            session['user_id'] = str(result.inserted_id)
            session['user_name'] = name
            session['user_email'] = email
            session['role'] = "user"

            flash(f"Account created successfully! Welcome to VAYELLE, {name}.", "success")
            return redirect(url_for('main.index'))
        except Exception as e:
            flash(f"Registration failed: {str(e)}", "error")
            return render_template('register.html', name=name, email=email, preferred_size=preferred_size)

    return render_template('register.html', user=get_current_user())

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        if session.get('role') == 'manager':
            return redirect(url_for('manager.dashboard'))
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not email or not password:
            flash("Please enter both email and password.", "error")
            return render_template('login.html', email=email)

        db_ok, db_msg = check_db_connection()
        if not db_ok:
            flash(f"Database error: {db_msg}. Please ensure MongoDB is running.", "error")
            return render_template('login.html', email=email)

        users_col = get_users_collection()
        if users_col is None:
            flash("Could not access users collection in database.", "error")
            return render_template('login.html', email=email)

        user_record = users_col.find_one({"email": email})
        if not user_record or not verify_password(user_record.get('password_hash', ''), password):
            flash("Invalid email or password. Please try again.", "error")
            return render_template('login.html', email=email)

        # Login success: set session
        session.permanent = remember
        session['user_id'] = str(user_record['_id'])
        session['user_name'] = user_record.get('name', 'User')
        session['user_email'] = user_record.get('email')
        session['role'] = user_record.get('role', 'user')

        flash(f"Welcome back, {session['user_name']}!", "success")

        # Redirect based on role or next parameter
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        if session['role'] == 'manager':
            return redirect(url_for('manager.dashboard'))
        return redirect(url_for('main.index'))

    return render_template('login.html', user=get_current_user())

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out successfully.", "default")
    return redirect(url_for('auth.login'))
