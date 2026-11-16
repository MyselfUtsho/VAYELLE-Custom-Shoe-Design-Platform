from datetime import datetime, timezone
import os
from bson import ObjectId
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app.db import get_shoes_collection, check_db_connection
from app.auth_utils import manager_required, get_current_user
from app.cloudinary_service import (
    is_cloudinary_configured,
    validate_uploaded_image,
    upload_shoe_image,
    upload_shoe_from_url,
    upload_preset_to_cloudinary
)

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
        db_status=db_msg,
        cloudinary_configured=is_cloudinary_configured()
    )

@manager_bp.route('/shoes/add', methods=['POST'])
@manager_required
def add_shoe():
    shoe_name = request.form.get('shoe_name', '').strip()
    category = request.form.get('category', '').strip()
    gender = request.form.get('gender', '').strip()
    description = request.form.get('description', '').strip()
    base_price_raw = request.form.get('base_price', '').strip()
    availability = request.form.get('availability', 'In Stock').strip()

    # Form text validation
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

    # Check database connection
    db_ok, db_msg = check_db_connection()
    if not db_ok:
        flash(f"Cannot save shoe: Database not reachable ({db_msg}).", "error")
        return redirect(url_for('manager.dashboard'))

    shoes_col = get_shoes_collection()
    if shoes_col is None:
        flash("Shoes collection unavailable.", "error")
        return redirect(url_for('manager.dashboard'))

    # Image inputs: Option A (Direct Upload) vs Option B (URL / Preset)
    shoe_file = request.files.get('shoe_image')
    image_url_input = request.form.get('image_url', '').strip()

    cloudinary_url = None
    upload_error = None
    is_testing = current_app.config.get('TESTING', False) and not current_app.config.get('STRICT_CLOUDINARY_TEST', False)

    # Option A: Direct File Upload takes priority if provided
    if shoe_file and shoe_file.filename:
        # Validate uploaded file (extension, 10MB limit, binary magic bytes)
        is_valid, val_err, _ = validate_uploaded_image(shoe_file)
        if not is_valid:
            flash(f"Image upload validation failed: {val_err}", "error")
            return redirect(url_for('manager.dashboard'))

        if is_testing:
            cloudinary_url = f"https://res.cloudinary.com/test-cloud/image/upload/c_limit,f_auto,h_800,q_auto,w_800/v1/vayelle/shoes/{os.path.basename(shoe_file.filename)}"
        elif not is_cloudinary_configured():
            flash("Cloudinary credentials are not configured in environment variables (CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET). Please configure them in your .env file to enable Cloudinary image delivery.", "error")
            return redirect(url_for('manager.dashboard'))
        else:
            cloudinary_url, upload_error = upload_shoe_image(shoe_file)

    # Option B: Public Image URL or Preset
    elif image_url_input:
        if is_testing:
            cloudinary_url = f"https://res.cloudinary.com/test-cloud/image/upload/c_limit,f_auto,h_800,q_auto,w_800/v1/vayelle/shoes/{os.path.basename(image_url_input)}"
        elif not is_cloudinary_configured():
            flash("Cloudinary credentials are not configured in environment variables. All shoe images must be uploaded to Cloudinary before saving to the catalog. Please configure your Cloudinary credentials in .env.", "error")
            return redirect(url_for('manager.dashboard'))
        else:
            # If it is a local preset path (e.g. /static/images/shoe-black-runner.jpg)
            if image_url_input.startswith('/static/images/') or image_url_input.startswith('static/images/'):
                cloudinary_url, upload_error = upload_preset_to_cloudinary(
                    image_url_input,
                    app_root=current_app.root_path
                )
            else:
                # External public image URL: download safely with SSRF protection and upload to Cloudinary
                cloudinary_url, upload_error = upload_shoe_from_url(image_url_input)

    else:
        flash("Please provide a shoe image: select an image file (Option A) or enter a public image URL / preset (Option B).", "error")
        return redirect(url_for('manager.dashboard'))

    # Handle upload failure
    if upload_error or not cloudinary_url:
        flash(f"Image processing failed: {upload_error}", "error")
        return redirect(url_for('manager.dashboard'))

    # Prepare shoe record for MongoDB insertion (always stores Cloudinary CDN URL)
    shoe_doc = {
        'shoe_name': shoe_name,
        'category': category,
        'gender': gender,
        'description': description,
        'base_price': base_price,
        'image_url': cloudinary_url,
        'availability': availability,
        'created_at': datetime.now(timezone.utc),
        'created_by': session.get('user_email', 'manager')
    }

    try:
        shoes_col.insert_one(shoe_doc)
        flash(f"Success! Shoe \"{shoe_name}\" has been added to MongoDB inventory with Cloudinary image delivery.", "success")
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
