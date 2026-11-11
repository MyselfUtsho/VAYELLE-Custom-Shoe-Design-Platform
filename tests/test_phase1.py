"""
Automated Test Suite for VAYELLE Phase 1
Verifies:
1. User registration with validation & unique email check
2. Password hashing with Werkzeug
3. Strict assignment of 'user' role on public registration
4. User login & session management
5. Role-based access control (Guest / User blocked from Manager routes)
6. Manager access to Dashboard
7. Manager adding a shoe to MongoDB collection 'shoes'
8. Shoe data persistence, retrieval, and inventory display
9. Deletion of shoe record from inventory
10. User logout
"""
import os
import sys
import unittest
from datetime import datetime, timezone

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import mongomock
from werkzeug.security import check_password_hash
from app import create_app
import app.db as db_module

class Phase1TestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SECRET_KEY'] = 'test-secret-key-123'
        self.client = self.app.test_client()

        # Mock MongoDB database for reproducible testing
        self.mock_client = mongomock.MongoClient()
        self.mock_db = self.mock_client['vayelle_test_db']
        
        # Patch db_module to use mock client
        self.orig_get_db_client = db_module.get_db_client
        self.orig_get_db = db_module.get_db
        self.orig_check = db_module.check_db_connection

        db_module.get_db_client = lambda: self.mock_client
        db_module.get_db = lambda: self.mock_db
        db_module.check_db_connection = lambda: (True, "Mock DB Connected")

        # Create unique index
        self.mock_db.users.create_index("email", unique=True)

    def tearDown(self):
        db_module.get_db_client = self.orig_get_db_client
        db_module.get_db = self.orig_get_db
        db_module.check_db_connection = self.orig_check

    def test_01_registration_success(self):
        """Test regular user registration creates record with hashed password and role='user'"""
        response = self.client.post('/register', data={
            'name': 'Test Student',
            'email': 'student@university.edu',
            'password': 'SecurePassword123',
            'confirm_password': 'SecurePassword123',
            'preferred_size': '42'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Verify in MongoDB
        user = self.mock_db.users.find_one({'email': 'student@university.edu'})
        self.assertIsNotNone(user)
        self.assertEqual(user['name'], 'Test Student')
        # Check role is strictly 'user'
        self.assertEqual(user['role'], 'user')
        # Check password is NOT plain text
        self.assertNotEqual(user['password_hash'], 'SecurePassword123')
        # Check Werkzeug hash validity
        self.assertTrue(check_password_hash(user['password_hash'], 'SecurePassword123'))

    def test_02_registration_duplicate_email_rejected(self):
        """Test registering with an existing email is rejected"""
        # Register first time
        self.client.post('/register', data={
            'name': 'First User',
            'email': 'duplicate@vayelle.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        })
        # Log out so the next registration attempt is treated as guest
        self.client.get('/logout')

        # Register second time with same email
        response = self.client.post('/register', data={
            'name': 'Second User',
            'email': 'duplicate@vayelle.com',
            'password': 'DifferentPassword',
            'confirm_password': 'DifferentPassword'
        }, follow_redirects=True)

        self.assertIn(b'already exists', response.data)
        # Should only be one user with that email
        count = self.mock_db.users.count_documents({'email': 'duplicate@vayelle.com'})
        self.assertEqual(count, 1)

    def test_03_registration_role_tampering_prevented(self):
        """Test that public registration cannot escalate role to 'manager'"""
        self.client.post('/register', data={
            'name': 'Attacker User',
            'email': 'attacker@vayelle.com',
            'password': 'Password123',
            'confirm_password': 'Password123',
            'role': 'manager'  # Attempted tampering
        })

        user = self.mock_db.users.find_one({'email': 'attacker@vayelle.com'})
        self.assertIsNotNone(user)
        # Role must still be 'user'
        self.assertEqual(user['role'], 'user')

    def test_04_user_login_and_logout(self):
        """Test login with valid credentials sets session, and logout clears it"""
        # Register user
        self.client.post('/register', data={
            'name': 'Login Tester',
            'email': 'login_tester@vayelle.com',
            'password': 'SecretPassword123',
            'confirm_password': 'SecretPassword123'
        })
        self.client.get('/logout')

        # Attempt login with invalid password
        res_fail = self.client.post('/login', data={
            'email': 'login_tester@vayelle.com',
            'password': 'WrongPassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password', res_fail.data)

        # Attempt login with correct password
        res_ok = self.client.post('/login', data={
            'email': 'login_tester@vayelle.com',
            'password': 'SecretPassword123'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back, Login Tester', res_ok.data)

        # Logout
        res_logout = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'signed out successfully', res_logout.data)

    def test_05_role_access_control(self):
        """Test that Guests and Regular Users cannot access Manager Dashboard"""
        # 1. Guest access
        res_guest = self.client.get('/manager/dashboard')
        self.assertEqual(res_guest.status_code, 302)
        self.assertIn('/login', res_guest.headers['Location'])

        # 2. Regular User access
        self.client.post('/register', data={
            'name': 'Normal User',
            'email': 'normal@vayelle.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        })
        # Try accessing manager dashboard as normal user
        res_user = self.client.get('/manager/dashboard', follow_redirects=True)
        self.assertIn(b'Access denied', res_user.data)

    def test_06_manager_dashboard_and_add_shoe(self):
        """Test manager logging in, opening dashboard, adding shoe to MongoDB, and viewing inventory"""
        # Setup manager account directly in DB (simulating `manage.py create-manager`)
        from app.auth_utils import hash_password
        self.mock_db.users.insert_one({
            'name': 'Platform Manager',
            'email': 'manager@vayelle.com',
            'password_hash': hash_password('ManagerPass123'),
            'role': 'manager',
            'created_at': datetime.now(timezone.utc)
        })

        # Login as manager
        login_res = self.client.post('/login', data={
            'email': 'manager@vayelle.com',
            'password': 'ManagerPass123'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)

        # Access Dashboard
        dash_res = self.client.get('/manager/dashboard')
        self.assertEqual(dash_res.status_code, 200)
        self.assertIn(b'Welcome, Platform Manager', dash_res.data)
        self.assertIn(b'Add New Shoe to Database', dash_res.data)

        # Submit Add Shoe form
        add_res = self.client.post('/manager/shoes/add', data={
            'shoe_name': 'Test Velvet Runner',
            'category': 'Sneakers',
            'gender': 'Unisex',
            'description': 'Premium velvet exterior sneaker designed for comfort.',
            'base_price': '3400',
            'availability': 'In Stock',
            'image_url': '/static/images/shoe-black-runner.jpg'
        }, follow_redirects=True)

        self.assertEqual(add_res.status_code, 200)
        self.assertIn(b'has been added to MongoDB inventory', add_res.data)

        # Verify shoe document in MongoDB collection 'shoes'
        shoe = self.mock_db.shoes.find_one({'shoe_name': 'Test Velvet Runner'})
        self.assertIsNotNone(shoe)
        self.assertEqual(shoe['category'], 'Sneakers')
        self.assertEqual(shoe['gender'], 'Unisex')
        self.assertEqual(shoe['base_price'], 3400.0)
        self.assertEqual(shoe['availability'], 'In Stock')
        self.assertEqual(shoe['created_by'], 'manager@vayelle.com')

        # Check inventory page shows the shoe
        inv_res = self.client.get('/manager/inventory')
        self.assertEqual(inv_res.status_code, 200)
        self.assertIn(b'Test Velvet Runner', inv_res.data)
        self.assertIn(b'3,400', inv_res.data)

        # Test deleting the shoe
        shoe_id = str(shoe['_id'])
        del_res = self.client.post(f'/manager/shoes/{shoe_id}/delete', follow_redirects=True)
        self.assertIn(b'deleted from inventory', del_res.data)
        self.assertIsNone(self.mock_db.shoes.find_one({'_id': shoe['_id']}))

if __name__ == '__main__':
    unittest.main()
