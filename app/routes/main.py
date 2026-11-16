from flask import Blueprint, render_template, request, redirect, url_for, session
from app.auth_utils import get_current_user
from app.db import get_shoes_collection, check_db_connection

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage route: displays hero section and featured collection."""
    user = get_current_user()
    db_ok, _ = check_db_connection()
    shoes_list = []
    
    if db_ok:
        shoes_col = get_shoes_collection()
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
    # An empty query dictionary {} retrieves all shoes
    query = {}
    
    # Filter by gender if a specific gender is selected (Men, Women, Unisex)
    if selected_gender and selected_gender != 'All':
        query['gender'] = selected_gender
        
    # Filter by shoe type / category if selected (Sneakers, Casual, Formal)
    if selected_category and selected_category != 'All':
        query['category'] = selected_category
        
    # Step 3: Connect to MongoDB and fetch matching shoe records
    shoes_list = []
    db_ok, db_msg = check_db_connection()
    
    if db_ok:
        shoes_col = get_shoes_collection()
        if shoes_col is not None:
            try:
                # Query MongoDB with our filter, sorting newest items first
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
    db_ok, db_msg = check_db_connection()

    if db_ok and error_message is None:
        shoes_col = get_shoes_collection()
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

@main_bp.route('/category')
def category():
    """
    Legacy route handler: redirects category requests to the main explore view.
    Maps gender categories (men, women, unisex) and types (sneakers, casual, formal).
    """
    cat = request.args.get('cat', '').strip().lower()
    
    # Map category parameter to gender or category filter
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
