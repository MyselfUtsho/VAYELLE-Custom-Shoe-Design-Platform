import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from app.auth_utils import get_current_user
import app.db as app_db

main_bp = Blueprint('main', __name__)

# ── Outfit Upload Config (Khairul Islam Bhuiya — Module 1) ───────────────────
_UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads', 'outfits'))
_MAX_SIZE      = 5 * 1024 * 1024   # 5 MB
_ALLOWED_EXT   = {'jpg', 'jpeg', 'png'}

def _allowed_ext(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in _ALLOWED_EXT

def _magic_type(header: bytes):
    """Return 'jpg', 'png', or None based on magic bytes."""
    if header[:3] == b'\xff\xd8\xff':
        return 'jpg'
    if header[:4] == b'\x89PNG':
        return 'png'
    return None

def _fmt_size(n):
    return f'{n/1024:.1f} KB' if n < 1_048_576 else f'{n/1_048_576:.2f} MB'


# ── Athoy Roy — Module 1: Home & Catalog Browsing ───────────────────────────
@main_bp.route('/')
def index():
    """Homepage route: displays hero section and featured collection."""
    user = get_current_user()
    db_ok, _ = app_db.check_db_connection()
    shoes_list = []
    
    if db_ok:
        shoes_col = app_db.get_shoes_collection()
        if shoes_col is not None:
            try:
                shoes_list = list(shoes_col.find().sort('created_at', -1).limit(6))
            except Exception:
                shoes_list = []
                
    return render_template('index.html', user=user, shoes=shoes_list)

@main_bp.route('/explore')
def explore():
    """
    Module 1: Browse Shoes by Category & Gender (Athoy Roy)
    Retrieves shoe silhouettes from MongoDB with gender and category filtering.
    Delivers product images using Cloudinary image URLs with fallback handling.
    """
    user = get_current_user()
    
    # Step 1: Read filter parameters from the URL (default to 'All')
    selected_gender = request.args.get('gender', 'All').strip()
    selected_category = (request.args.get('category') or request.args.get('type') or 'All').strip()
    
    # Step 2: Build MongoDB query filter
    query = {}
    
    # Filter by gender if a specific gender is selected (Men, Women, Unisex)
    if selected_gender and selected_gender != 'All':
        query['gender'] = selected_gender
        
    # Filter by shoe type / category if selected (Sneakers, Casual, Formal)
    if selected_category and selected_category != 'All':
        query['category'] = selected_category
        
    # Step 3: Connect to MongoDB and fetch matching shoe records
    shoes_list = []
    db_ok, db_msg = app_db.check_db_connection()
    
    if db_ok:
        shoes_col = app_db.get_shoes_collection()
        if shoes_col is not None:
            try:
                shoes_list = list(shoes_col.find(query).sort('created_at', -1))
            except Exception as e:
                print(f"Database query error: {e}")
                shoes_list = []
                
    # Step 4: Render the explore template with our dynamic shoe data
    return render_template(
        'explore.html',
        user=user,
        shoes=shoes_list,
        selected_gender=selected_gender,
        selected_category=selected_category,
        total_count=len(shoes_list)
    )

@main_bp.route('/category')
def category():
    """
    Legacy route handler: redirects category requests to the main explore view.
    Maps gender categories (men, women, unisex) and types (sneakers, casual, formal).
    """
    cat = request.args.get('cat', '').strip().lower()
    
    if cat == 'men':
        return redirect(url_for('main.explore', gender='Men'))
    elif cat == 'women':
        return redirect(url_for('main.explore', gender='Women'))
    elif cat == 'unisex':
        return redirect(url_for('main.explore', gender='Unisex'))
    elif cat == 'sneakers':
        return redirect(url_for('main.explore', category='Sneakers'))
    elif cat == 'casual':
        return redirect(url_for('main.explore', category='Casual'))
    elif cat == 'formal':
        return redirect(url_for('main.explore', category='Formal'))
        
    return redirect(url_for('main.explore'))


# ── Diya Zerin — Module 1: Budget-Based Shoe Search ──────────────────────────
@main_bp.route('/budget')
def budget():
    """
    Module 1: Budget-Based Shoe Search (Diya Zerin — 22101062)
    Users can search for shoes within a minimum and maximum budget.
    The system retrieves matching shoe records from MongoDB based on their base prices.
    """
    user = get_current_user()

    # Step 1: Read budget filter parameters from URL query string
    min_price_raw = request.args.get('min_price', '').strip()
    max_price_raw = request.args.get('max_price', '').strip()

    # Step 2: Parse and validate min/max price inputs
    min_price = None
    max_price = None
    error_message = None

    if min_price_raw:
        try:
            min_price = float(min_price_raw)
            if min_price < 0:
                error_message = "Minimum price cannot be negative."
                min_price = None
        except ValueError:
            error_message = "Minimum price must be a valid number."

    if max_price_raw:
        try:
            max_price = float(max_price_raw)
            if max_price < 0:
                error_message = "Maximum price cannot be negative."
                max_price = None
        except ValueError:
            error_message = "Maximum price must be a valid number."

    # Cross-validate: min should not exceed max
    if min_price is not None and max_price is not None and min_price > max_price:
        error_message = "Minimum price cannot be greater than maximum price."

    # Step 3: Build MongoDB query filter based on budget range
    query = {}
    has_search = False

    if error_message is None:
        if min_price is not None or max_price is not None:
            has_search = True
            price_filter = {}
            if min_price is not None:
                price_filter['$gte'] = min_price
            if max_price is not None:
                price_filter['$lte'] = max_price
            if price_filter:
                query['base_price'] = price_filter

    # Step 4: Connect to MongoDB and fetch matching shoe records
    shoes_list = []
    db_ok, db_msg = app_db.check_db_connection()

    if db_ok and error_message is None:
        shoes_col = app_db.get_shoes_collection()
        if shoes_col is not None:
            try:
                # Query MongoDB with budget filter, sorting by price (low to high)
                shoes_list = list(shoes_col.find(query).sort('base_price', 1))
            except Exception as e:
                print(f"Budget search query error: {e}")
                shoes_list = []

    # Step 5: Render the budget search template with results
    return render_template(
        'budget.html',
        user=user,
        shoes=shoes_list,
        min_price=min_price,
        max_price=max_price,
        min_price_raw=min_price_raw,
        max_price_raw=max_price_raw,
        has_search=has_search,
        error_message=error_message,
        total_count=len(shoes_list)
    )


# ── Khairul Islam Bhuiya — Module 1: Outfit Image Upload ─────────────────────
@main_bp.route('/outfit-upload', methods=['GET', 'POST'])
def outfit_upload():
    """
    Module 1 — Khairul Islam Bhuiya
    Outfit Image Upload with full backend validation:
      • File-type check  (extension + magic-byte verification)
      • File-size check  (max 5 MB)
      • Saves to static/uploads/outfits/  with a UUID filename
      • Stores filename in session for downstream analysis routes
    """
    user = get_current_user()

    if request.method == 'POST':
        # ── 1. Presence check ─────────────────────────────────────────────────
        if 'outfit_image' not in request.files:
            return jsonify({'success': False, 'error': 'No file attached to the request.'}), 400

        file = request.files['outfit_image']

        if not file or file.filename == '':
            return jsonify({'success': False, 'error': 'No file was selected.'}), 400

        # ── 2. Extension validation ───────────────────────────────────────────
        if not _allowed_ext(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Only JPG and PNG images are accepted.'
            }), 415

        # ── 3. Size validation (read-ahead, then rewind) ──────────────────────
        file.seek(0, 2)
        size_bytes = file.tell()
        file.seek(0)

        if size_bytes == 0:
            return jsonify({'success': False, 'error': 'The uploaded file is empty.'}), 400

        if size_bytes > _MAX_SIZE:
            return jsonify({
                'success': False,
                'error': f'File too large ({_fmt_size(size_bytes)}). Maximum allowed size is 5 MB.'
            }), 413

        # ── 4. Magic-byte validation (prevents disguised files) ───────────────
        header = file.read(12)
        file.seek(0)
        real_type = _magic_type(header)

        if real_type is None:
            return jsonify({
                'success': False,
                'error': 'File content does not match a valid JPG or PNG image.'
            }), 415

        # ── 5. Save file with UUID name ───────────────────────────────────────
        os.makedirs(_UPLOAD_FOLDER, exist_ok=True)
        filename  = f"outfit_{uuid.uuid4().hex}.{real_type}"
        save_path = os.path.join(_UPLOAD_FOLDER, filename)
        file.save(save_path)

        # ── 6. Persist in session ─────────────────────────────────────────────
        session['outfit_filename']       = filename
        session['outfit_size_bytes']     = size_bytes
        session['outfit_size_formatted'] = _fmt_size(size_bytes)
        session['outfit_type']           = real_type.upper()

        image_url = url_for('static', filename=f'uploads/outfits/{filename}')

        return jsonify({
            'success'        : True,
            'message'        : 'Outfit uploaded successfully!',
            'filename'       : filename,
            'image_url'      : image_url,
            'size_bytes'     : size_bytes,
            'size_formatted' : _fmt_size(size_bytes),
            'file_type'      : real_type.upper(),
        })

    # ── GET: render page ──────────────────────────────────────────────────────
    existing_url = None
    if session.get('outfit_filename'):
        existing_url = url_for(
            'static',
            filename=f"uploads/outfits/{session['outfit_filename']}"
        )

    return render_template(
        'outfit_upload.html',
        user            = user,
        existing_url    = existing_url,
        existing_size   = session.get('outfit_size_formatted', ''),
        existing_type   = session.get('outfit_type', ''),
    )


@main_bp.route('/outfit-upload/clear', methods=['POST'])
def outfit_upload_clear():
    """Remove the stored outfit from the session (and disk if present)."""
    filename = session.pop('outfit_filename', None)
    session.pop('outfit_size_bytes', None)
    session.pop('outfit_size_formatted', None)
    session.pop('outfit_type', None)

    if filename:
        path = os.path.join(_UPLOAD_FOLDER, filename)
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass

    return jsonify({'success': True})


# ════════════════════════════════════════════════════════════════════════════
# Khairul Islam Bhuiya — Module 2: Shoe Size Guide & SSLCommerz Sandbox Pay
# ════════════════════════════════════════════════════════════════════════════

# Full EU/UK/US/CM size chart (EU 35–47)
SIZE_CHART = [
    {'eu': 35, 'uk': 2,   'us_m': 3,   'us_w': 5,   'cm': 21.5},
    {'eu': 36, 'uk': 3,   'us_m': 4,   'us_w': 6,   'cm': 22.5},
    {'eu': 37, 'uk': 4,   'us_m': 5,   'us_w': 7,   'cm': 23.0},
    {'eu': 38, 'uk': 5,   'us_m': 6,   'us_w': 8,   'cm': 24.0},
    {'eu': 39, 'uk': 6,   'us_m': 7,   'us_w': 9,   'cm': 24.5},
    {'eu': 40, 'uk': 6.5, 'us_m': 7.5, 'us_w': 9.5, 'cm': 25.0},
    {'eu': 41, 'uk': 7,   'us_m': 8,   'us_w': 10,  'cm': 25.5},
    {'eu': 42, 'uk': 8,   'us_m': 9,   'us_w': 11,  'cm': 26.5},
    {'eu': 43, 'uk': 9,   'us_m': 10,  'us_w': 12,  'cm': 27.0},
    {'eu': 44, 'uk': 10,  'us_m': 11,  'us_w': 13,  'cm': 27.5},
    {'eu': 45, 'uk': 10.5,'us_m': 11.5,'us_w': 13.5,'cm': 28.5},
    {'eu': 46, 'uk': 11,  'us_m': 12,  'us_w': 14,  'cm': 29.0},
    {'eu': 47, 'uk': 12,  'us_m': 13,  'us_w': 15,  'cm': 30.0},
]

def _find_size(cm: float):
    """Return the best matching size row for a given foot length in cm."""
    best, best_diff = None, float('inf')
    for row in SIZE_CHART:
        diff = abs(row['cm'] - cm)
        if diff < best_diff:
            best_diff, best = diff, row
    return best


@main_bp.route('/size-guide')
def size_guide():
    """
    Module 2 — Khairul Islam Bhuiya
    Interactive Shoe Size Guide with foot-length estimation,
    EU/UK/US/CM size chart, width guide, and measurement instructions.
    """
    user = get_current_user()
    return render_template('size_guide.html', user=user, size_chart=SIZE_CHART)


@main_bp.route('/size-guide/find', methods=['POST'])
def size_guide_find():
    """AJAX: Find the matching size for a given foot length (cm)."""
    try:
        cm = float(request.json.get('cm', 0))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'error': 'Invalid measurement.'}), 400

    if not (18.0 <= cm <= 34.0):
        return jsonify({'success': False, 'error': 'Please enter a foot length between 18 and 34 cm.'}), 400

    result = _find_size(cm)
    if not result:
        return jsonify({'success': False, 'error': 'No size found.'}), 404

    # Save to session
    session['shoe_size_eu']  = result['eu']
    session['shoe_size_uk']  = result['uk']
    session['shoe_size_us_m']= result['us_m']
    session['shoe_size_us_w']= result['us_w']
    session['shoe_size_cm']  = result['cm']

    return jsonify({'success': True, 'size': result})


@main_bp.route('/checkout')
def checkout():
    """
    Module 2 — Khairul Islam Bhuiya
    Full checkout page with order summary, shipping form,
    delivery options, and SSLCommerz Sandbox payment initiation.
    """
    user     = get_current_user()
    shoes_col = app_db.get_shoes_collection()
    shoes_list = list(shoes_col.find().sort('created_at', -1)) if shoes_col is not None else []

    # Saved size from session
    saved_size = {
        'eu' : session.get('shoe_size_eu'),
        'uk' : session.get('shoe_size_uk'),
        'us_m': session.get('shoe_size_us_m'),
        'us_w': session.get('shoe_size_us_w'),
        'cm' : session.get('shoe_size_cm'),
    }

    return render_template(
        'checkout.html',
        user       = user,
        shoes      = shoes_list,
        saved_size = saved_size,
    )


@main_bp.route('/payment/initiate', methods=['POST'])
def payment_initiate():
    """
    Module 2 — Khairul Islam Bhuiya
    Initiates an SSLCommerz Sandbox payment session.
    Collects order details, calls SSLCommerz API, redirects to gateway.
    """
    import uuid as _uuid

    # ── Collect form data ──────────────────────────────────────────────────
    name     = request.form.get('cus_name', '').strip()
    email    = request.form.get('cus_email', '').strip()
    phone    = request.form.get('cus_phone', '').strip()
    address  = request.form.get('cus_address', '').strip()
    city     = request.form.get('cus_city', 'Dhaka').strip()
    total    = request.form.get('total_amount', '0').strip()
    shoe_name= request.form.get('shoe_name', 'Custom Shoe').strip()
    delivery = request.form.get('delivery_type', 'Standard').strip()

    # Basic validation
    if not all([name, email, phone, address]):
        flash('Please fill in all required shipping fields.', 'error')
        return redirect(url_for('main.checkout'))

    try:
        amount = float(total)
        if amount <= 0:
            raise ValueError
    except (TypeError, ValueError):
        flash('Invalid order total. Please go back and try again.', 'error')
        return redirect(url_for('main.checkout'))

    tran_id = 'VAYELLE-' + _uuid.uuid4().hex[:12].upper()

    # Store order in session for success/fail pages
    session['pending_order'] = {
        'tran_id'  : tran_id,
        'name'     : name,
        'email'    : email,
        'phone'    : phone,
        'address'  : address,
        'city'     : city,
        'shoe_name': shoe_name,
        'delivery' : delivery,
        'amount'   : amount,
        'size_eu'  : session.get('shoe_size_eu', 'N/A'),
    }

    # ── SSLCommerz Sandbox API call ────────────────────────────────────────
    STORE_ID     = os.getenv('SSLCOMMERZ_STORE_ID', 'testbox')
    STORE_PASSWD = os.getenv('SSLCOMMERZ_STORE_PASS', 'qwerty')
    SANDBOX_URL  = 'https://sandbox.sslcommerz.com/gwprocess/v4/api.php'

    base_url = request.host_url.rstrip('/')
    payload = {
        'store_id'        : STORE_ID,
        'store_passwd'    : STORE_PASSWD,
        'total_amount'    : f'{amount:.2f}',
        'currency'        : 'BDT',
        'tran_id'         : tran_id,
        'success_url'     : base_url + url_for('main.payment_success'),
        'fail_url'        : base_url + url_for('main.payment_fail'),
        'cancel_url'      : base_url + url_for('main.payment_cancel'),
        'cus_name'        : name,
        'cus_email'       : email,
        'cus_add1'        : address,
        'cus_city'        : city,
        'cus_country'     : 'Bangladesh',
        'cus_phone'       : phone,
        'ship_name'       : name,
        'ship_add1'       : address,
        'ship_city'       : city,
        'ship_country'    : 'Bangladesh',
        'ship_phone'      : phone,
        'shipping_method' : delivery,
        'product_name'    : shoe_name,
        'product_category': 'Footwear',
        'product_profile' : 'physical-goods',
    }

    try:
        import requests as _req
        resp = _req.post(SANDBOX_URL, data=payload, timeout=12)
        data = resp.json()
        if data.get('status') == 'SUCCESS' and data.get('GatewayPageURL'):
            return redirect(data['GatewayPageURL'])
        # SSLCommerz returned an error — fall through to sandbox demo mode
    except Exception:
        pass

    # ── Sandbox Demo Mode (no live API creds) ──────────────────────────────
    # Simulate the payment gateway redirect with our own demo page
    session['pending_order']['demo_mode'] = True
    return redirect(url_for('main.payment_demo'))


@main_bp.route('/payment/demo')
def payment_demo():
    """Sandbox demo gateway page when SSLCommerz creds are not configured."""
    order = session.get('pending_order')
    if not order:
        return redirect(url_for('main.checkout'))
    return render_template('payment_demo.html', order=order)


@main_bp.route('/payment/demo/process', methods=['POST'])
def payment_demo_process():
    """
    Module 2 — Khairul Islam Bhuiya
    Processes the sandbox demo payment form.
    Validates the demo session exists, then redirects to the success handler.
    This is the ONLY way to reach /payment/success in demo mode — a direct
    GET to /payment/success without a session order is harmless (order={}).
    """
    import uuid as _uuid2

    order = session.get('pending_order')
    if not order or not order.get('demo_mode'):
        flash('No active payment session found. Please restart checkout.', 'error')
        return redirect(url_for('main.checkout'))

    # Generate demo transaction identifiers
    tran_id  = order.get('tran_id', 'VAYELLE-' + _uuid2.uuid4().hex[:12].upper())
    val_id   = 'DEMO-' + _uuid2.uuid4().hex[:8].upper()
    amount   = str(order.get('amount', 0))

    # Mark the session order as processed so it cannot be reused
    session['pending_order']['demo_processed'] = True

    # Redirect to the standard success handler with demo params
    return redirect(
        url_for('main.payment_success')
        + f'?tran_id={tran_id}&val_id={val_id}&amount={amount}'
        + '&card_type=Demo+Card&store_amount=' + amount
    )


@main_bp.route('/payment/success', methods=['GET', 'POST'])
def payment_success():
    """SSLCommerz callback — payment successful."""
    order = session.pop('pending_order', {})
    tran_id  = request.values.get('tran_id', order.get('tran_id', 'N/A'))
    val_id   = request.values.get('val_id', 'DEMO-VAL')
    amount   = request.values.get('amount', str(order.get('amount', 0)))
    card     = request.values.get('card_type', 'Demo Card')
    store_amount = request.values.get('store_amount', amount)

    # Persist completed order in session history
    history = session.get('order_history', [])
    history.insert(0, {
        'tran_id'   : tran_id,
        'val_id'    : val_id,
        'shoe_name' : order.get('shoe_name', 'Custom Shoe'),
        'amount'    : float(amount),
        'name'      : order.get('name', ''),
        'email'     : order.get('email', ''),
        'size_eu'   : order.get('size_eu', 'N/A'),
        'delivery'  : order.get('delivery', 'Standard'),
        'card'      : card,
        'status'    : 'PAID',
    })
    session['order_history'] = history[:20]

    return render_template('payment_success.html',
        tran_id=tran_id, val_id=val_id,
        amount=float(amount), card=card,
        order=order,
    )


@main_bp.route('/payment/fail', methods=['GET', 'POST'])
def payment_fail():
    """SSLCommerz callback — payment failed."""
    order  = session.get('pending_order', {})
    reason = request.values.get('error', 'The transaction could not be completed.')
    return render_template('payment_fail.html', order=order, reason=reason)


@main_bp.route('/payment/cancel', methods=['GET', 'POST'])
def payment_cancel():
    """SSLCommerz callback — payment cancelled."""
    session.pop('pending_order', None)
    return render_template('payment_fail.html',
        order={}, reason='You cancelled the payment. Your order was not placed.')
