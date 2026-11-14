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
