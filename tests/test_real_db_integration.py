"""
VAYELLE - Real MongoDB End-to-End Integration Test Suite
Executes real database operations against mongodb://127.0.0.1:27017/vayelle_db
Validates:
1. Real MongoDB ping & collection availability
2. User registration and real document persistence
3. Password hashing with Werkzeug
4. Role tampering prevention (role='user')
5. Duplicate registration rejection
6. User authentication, session management, and logout
7. Role-based access control (Guests & Users blocked from Manager routes)
8. Manager initialization via create_manager
9. Manager login and Dashboard access
10. Adding a shoe through the Manager form and verifying MongoDB persistence
11. Manager Inventory view retrieval
"""
import os
import sys
from datetime import datetime, timezone

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)

from app import create_app
from app.db import get_db, get_users_collection, get_shoes_collection, check_db_connection
from app.auth_utils import verify_password
from manage import create_manager

def run_real_db_tests():
    print("=" * 75)
    print("VAYELLE - REAL MONGODB INTEGRATION TEST SUITE (127.0.0.1:27017)")
    print("=" * 75)

    # 1. Verify Database Connection
    print("\n[STEP 1] Testing Real MongoDB Connection...")
    connected, msg = check_db_connection()
    if not connected:
        print(f"[FAIL] MongoDB connection failed: {msg}")
        return False
    print(f"[PASS] {msg}")

    db = get_db()
    users_col = get_users_collection()
    shoes_col = get_shoes_collection()
    print(f"       Database: {db.name}")
    print(f"       Collections: users ({users_col.count_documents({})}), shoes ({shoes_col.count_documents({})})")

    # Clean previous test records if any to make test idempotent
    users_col.delete_many({"email": {"$in": [
        "audit_user@vayelle.com", 
        "tamper_user@vayelle.com", 
        "audit_manager@vayelle.com"
    ]}})
    shoes_col.delete_many({"shoe_name": "Aero Flow Runner"})

    # Setup Flask test client
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    client = app.test_client()

    # 2. Test User Registration
    print("\n[STEP 2] Testing User Registration & Real MongoDB Persistence...")
    reg_res = client.post('/register', data={
        'name': 'Audit Test User',
        'email': 'audit_user@vayelle.com',
        'password': 'UserPassword123',
        'confirm_password': 'UserPassword123',
        'preferred_size': '41'
    }, follow_redirects=True)
    assert reg_res.status_code == 200, f"Registration failed HTTP {reg_res.status_code}"

    # Verify document in real MongoDB
    user_doc = users_col.find_one({"email": "audit_user@vayelle.com"})
    assert user_doc is not None, "User document was not found in real MongoDB users collection!"
    assert user_doc['name'] == 'Audit Test User'
    assert user_doc['role'] == 'user', f"Expected role 'user', got {user_doc['role']}"
    assert user_doc['password_hash'] != 'UserPassword123', "Password was saved in plain text!"
    assert verify_password(user_doc['password_hash'], 'UserPassword123'), "Werkzeug password hash verification failed!"
    print(f"[PASS] User document saved in MongoDB: _id={user_doc['_id']}, role={user_doc['role']}")
    print(f"       Password securely hashed with Werkzeug: {user_doc['password_hash'][:25]}...")

    # Log out user
    client.get('/logout')

    # 3. Test Duplicate Registration
    print("\n[STEP 3] Testing Duplicate Registration Rejection...")
    dup_res = client.post('/register', data={
        'name': 'Duplicate User',
        'email': 'audit_user@vayelle.com',
        'password': 'AnotherPassword123',
        'confirm_password': 'AnotherPassword123'
    }, follow_redirects=True)
    assert b"already exists" in dup_res.data, "Duplicate email was not rejected!"
    count = users_col.count_documents({"email": "audit_user@vayelle.com"})
    assert count == 1, f"Expected 1 user, found {count} in MongoDB!"
    print("[PASS] Duplicate registration rejected and prevented duplicate MongoDB document.")

    # 4. Test Role Tampering Prevention
    print("\n[STEP 4] Testing Role Tampering Prevention on Public Registration...")
    tamper_res = client.post('/register', data={
        'name': 'Tamper User',
        'email': 'tamper_user@vayelle.com',
        'password': 'TamperPassword123',
        'confirm_password': 'TamperPassword123',
        'role': 'manager'  # Malicious attempt
    }, follow_redirects=True)
    tamper_doc = users_col.find_one({"email": "tamper_user@vayelle.com"})
    assert tamper_doc is not None
    assert tamper_doc['role'] == 'user', f"Security flaw: Role tampering succeeded! Role={tamper_doc['role']}"
    print("[PASS] Role escalation thwarted: Public registration strictly assigned role='user'.")
    client.get('/logout')

    # 5. Test Login, Session Handling & Logout
    print("\n[STEP 5] Testing Login, Session Management, and Logout...")
    # Bad password
    bad_login = client.post('/login', data={
        'email': 'audit_user@vayelle.com',
        'password': 'WrongPassword!'
    }, follow_redirects=True)
    assert b"Invalid email or password" in bad_login.data
    print("[PASS] Invalid password rejected.")

    # Good password
    good_login = client.post('/login', data={
        'email': 'audit_user@vayelle.com',
        'password': 'UserPassword123'
    }, follow_redirects=True)
    assert b"Welcome back, Audit Test User" in good_login.data
    print("[PASS] Valid credentials accepted. Session cookie established.")

    # 6. Test Role-Based Access Control
    print("\n[STEP 6] Testing Role-Based Access Control...")
    # As logged-in regular user, attempt to access Manager Dashboard
    forbidden_res = client.get('/manager/dashboard', follow_redirects=True)
    assert b"Access denied" in forbidden_res.data, "Regular user was not denied manager access!"
    print("[PASS] Regular user blocked from Manager Dashboard with 'Access denied' redirect.")

    # Logout
    logout_res = client.get('/logout', follow_redirects=True)
    assert b"signed out successfully" in logout_res.data
    print("[PASS] Logout terminated session successfully.")

    # As guest, attempt to access Manager Dashboard
    guest_res = client.get('/manager/dashboard')
    assert guest_res.status_code == 302, f"Expected 302 redirect for guest, got {guest_res.status_code}"
    assert '/login' in guest_res.headers['Location']
    print("[PASS] Unauthenticated guest redirected to login.")

    # 7. Initialize Manager Account
    print("\n[STEP 7] Initializing Manager Account in Real MongoDB...")
    create_manager(
        name="Audit Manager",
        email="audit_manager@vayelle.com",
        password="ManagerSecure2026!"
    )
    mgr_doc = users_col.find_one({"email": "audit_manager@vayelle.com"})
    assert mgr_doc is not None, "Manager document not found in MongoDB!"
    assert mgr_doc['role'] == 'manager', f"Expected role 'manager', got {mgr_doc['role']}"
    assert verify_password(mgr_doc['password_hash'], "ManagerSecure2026!"), "Manager password verification failed!"
    print(f"[PASS] Manager initialized: email={mgr_doc['email']}, role={mgr_doc['role']}")

    # 8. Test Manager Login & Dashboard
    print("\n[STEP 8] Testing Manager Login & Dashboard...")
    mgr_login = client.post('/login', data={
        'email': 'audit_manager@vayelle.com',
        'password': 'ManagerSecure2026!'
    }, follow_redirects=True)
    assert mgr_login.status_code == 200
    assert b"Welcome, Audit Manager" in mgr_login.data
    assert b"Add New Shoe to Database" in mgr_login.data
    print("[PASS] Manager authenticated successfully and Dashboard rendered.")

    # 9. Test Add Shoe & Real MongoDB Persistence
    print("\n[STEP 9] Testing Add Shoe Form & Real MongoDB Persistence...")
    add_res = client.post('/manager/shoes/add', data={
        'shoe_name': 'Aero Flow Runner',
        'category': 'Sneakers',
        'gender': 'Unisex',
        'base_price': '4500',
        'availability': 'In Stock',
        'description': 'Engineered lightweight mesh with dynamic street cushioning.',
        'image_url': '/static/images/shoe-black-runner.jpg'
    }, follow_redirects=True)
    assert add_res.status_code == 200
    assert b"has been added to MongoDB inventory" in add_res.data

    # Query real MongoDB collection 'shoes'
    shoe_doc = shoes_col.find_one({"shoe_name": "Aero Flow Runner"})
    assert shoe_doc is not None, "Shoe document was not found in MongoDB shoes collection!"
    assert shoe_doc['category'] == 'Sneakers'
    assert shoe_doc['gender'] == 'Unisex'
    assert shoe_doc['base_price'] == 4500.0
    assert shoe_doc['created_by'] == 'audit_manager@vayelle.com'
    print(f"[PASS] Shoe saved in MongoDB: _id={shoe_doc['_id']}, name={shoe_doc['shoe_name']}, price=BDT {shoe_doc['base_price']}")

    # 10. Test Manager Inventory Retrieval
    print("\n[STEP 10] Testing Manager Inventory Display...")
    inv_res = client.get('/manager/inventory')
    assert inv_res.status_code == 200
    assert b"Aero Flow Runner" in inv_res.data
    assert b"4,500" in inv_res.data
    print("[PASS] Inventory table correctly retrieved and rendered real MongoDB records.")

    print("\n" + "=" * 75)
    print("ALL REAL MONGODB INTEGRATION TESTS PASSED SUCCESSFULLY (10/10)")
    print("=" * 75)
    return True

if __name__ == '__main__':
    success = run_real_db_tests()
    sys.exit(0 if success else 1)
