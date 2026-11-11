import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-dev-secret-key-cse471')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/vayelle_db')
    DB_NAME = os.getenv('DB_NAME', 'vayelle_db')
    DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'
    
    # Session cookie security settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds
