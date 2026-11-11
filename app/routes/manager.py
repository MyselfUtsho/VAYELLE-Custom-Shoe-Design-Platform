from datetime import datetime, timezone
from bson import ObjectId
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.db import get_shoes_collection, check_db_connection
from app.auth_utils import manager_required, get_current_user

manager_bp = Blueprint('manager', __name__, url_prefix='/manager')

@manager_bp.route('/dashboard')
@manager_required
def dashboard():
    user = get_current_user()
    db_ok, db_msg = check_db_connection()
    shoes_list = []
    stats = {
        'total_shoes': 0,
        'categories_count': 0,
        'in_stock_count': 0
    }

    if db_ok:
        shoes_col = get_shoes_collection()
        if shoes_col is not None:
            try:
                shoes_list = list(shoes_col.find().sort('created_at', -1))
                stats['total_shoes'] = len(shoes_list)
                categories = set(s.get('category') for s in shoes_list if s.get('category'))
                stats['categories_count'] = len(categories)
                stats['in_stock_count'] = sum(1 for s in shoes_list if s.get('availability') in ['In Stock', True, 'true'])
            except Exception as e:
                flash(f"Error fetching inventory: {str(e)}", "error")

    return render_template(
        'manager/dashboard.html',
        user=user,
        shoes=shoes_list,
        stats=stats,
        db_connected=db_ok,
        db_status=db_msg
    )

@manager_bp.route('/shoes/add', methods=['POST'])
@manager_required
def add_shoe():
    shoe_name = request.form.get('shoe_name', '').strip()
    category = request.form.get('category', '').strip()
    gender = request.form.get('gender', '').strip()
    description = request.form.get('description', '').strip()
    base_price_raw = request.form.get('base_price', '').strip()
    image_url = request.form.get('image_url', '').strip()
    availability = request.form.get('availability', 'In Stock').strip()

    # Form validation
    if not shoe_name or not category or not gender or not base_price_raw:
        flash("Shoe name, category, gender, and base price are required.", "error")
        return redirect(url_for('manager.dashboard'))

    try:
        base_price = float(base_price_raw)
        if base_price <= 0:
            raise ValueError()
    except ValueError:
        flash("Base price must be a positive number.", "error")
        return redirect(url_for('manager.dashboard'))

    # Default image if empty
    if not image_url:
        image_url = '/static/images/shoe-black-runner.jpg'

    db_ok, db_msg = check_db_connection()
    if not db_ok:
        flash(f"Cannot save shoe: Database not reachable ({db_msg}).", "error")
        return redirect(url_for('manager.dashboard'))

    shoes_col = get_shoes_collection()
    if shoes_col is None:
        flash("Shoes collection unavailable.", "error")
        return redirect(url_for('manager.dashboard'))

    shoe_doc = {
        'shoe_name': shoe_name,
        'category': category,
        'gender': gender,
        'description': description,
        'base_price': base_price,
        'image_url': image_url,
        'availability': availability,
        'created_at': datetime.now(timezone.utc),
        'created_by': session.get('user_email', 'manager')
    }

    try:
        shoes_col.insert_one(shoe_doc)
        flash(f"Success! Shoe \"{shoe_name}\" has been added to MongoDB inventory.", "success")
    except Exception as e:
        flash(f"Failed to insert shoe record: {str(e)}", "error")

    return redirect(url_for('manager.dashboard'))

@manager_bp.route('/inventory')
@manager_required
def inventory():
    user = get_current_user()
    db_ok, db_msg = check_db_connection()
    shoes_list = []

    if db_ok:
        shoes_col = get_shoes_collection()
        if shoes_col is not None:
            try:
                shoes_list = list(shoes_col.find().sort('created_at', -1))
            except Exception as e:
                flash(f"Error reading inventory: {str(e)}", "error")

    return render_template(
        'manager/inventory.html',
        user=user,
        shoes=shoes_list,
        db_connected=db_ok,
        db_status=db_msg
    )

@manager_bp.route('/shoes/<shoe_id>/delete', methods=['POST'])
@manager_required
def delete_shoe(shoe_id):
    db_ok, _ = check_db_connection()
    if not db_ok:
        flash("Database error: cannot delete record.", "error")
        return redirect(url_for('manager.dashboard'))

    shoes_col = get_shoes_collection()
    if shoes_col is not None:
        try:
            res = shoes_col.delete_one({'_id': ObjectId(shoe_id)})
            if res.deleted_count > 0:
                flash("Shoe record deleted from inventory.", "default")
            else:
                flash("Shoe record not found.", "warning")
        except Exception as e:
            flash(f"Delete failed: {str(e)}", "error")

    return redirect(url_for('manager.dashboard'))
