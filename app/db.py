import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import Config

logger = logging.getLogger(__name__)

_client = None
_db = None

def get_db_client():
    """Initializes and caches the MongoDB client."""
    global _client
    if _client is None:
        try:
            kwargs = {'serverSelectionTimeoutMS': 5000}
            uri = Config.MONGO_URI
            if 'mongodb+srv://' in uri or 'ssl=true' in uri.lower() or 'tls=true' in uri.lower():
                try:
                    import certifi
                    kwargs['tlsCAFile'] = certifi.where()
                except ImportError:
                    pass
            _client = MongoClient(uri, **kwargs)
        except Exception as e:
            logger.error(f"Error creating MongoClient: {e}")
            return None
    return _client

def get_db():
    """Returns the database instance."""
    global _db
    if _db is None:
        client = get_db_client()
        if client is not None:
            _db = client[Config.DB_NAME]
            # Ensure unique index on email
            try:
                _db.users.create_index("email", unique=True)
                _db.shoes.create_index("created_at")
            except Exception as e:
                logger.warning(f"Could not initialize indexes: {e}")
    return _db

def check_db_connection():
    """Checks whether the database connection is alive and reachable.
    Returns (True, 'Connected') or (False, error_message).
    """
    try:
        client = get_db_client()
        if client is None:
            return False, "MongoClient initialization failed."
        # Ping the server
        client.admin.command('ping')
        return True, "MongoDB connected successfully."
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        return False, f"Could not connect to MongoDB: {str(e)}"
    except Exception as e:
        return False, f"Database error: {str(e)}"

def get_users_collection():
    db = get_db()
    return db.users if db is not None else None

def get_shoes_collection():
    db = get_db()
    return db.shoes if db is not None else None
