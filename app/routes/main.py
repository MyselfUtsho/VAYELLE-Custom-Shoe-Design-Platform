from flask import Blueprint, render_template, session
from app.auth_utils import get_current_user
from app.db import get_shoes_collection, check_db_connection

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
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
