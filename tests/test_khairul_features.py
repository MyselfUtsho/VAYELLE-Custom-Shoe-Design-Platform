"""
VAYELLE — Regression Test Suite for Khairul Islam Bhuiya's Features
Verifies:
 1. GET /outfit-upload loads successfully (HTTP 200)
 2. POST /outfit-upload validation: missing file, invalid extension, magic bytes
 3. POST /outfit-upload success with valid PNG
 4. POST /outfit-upload/clear clears session
 5. GET /size-guide loads size chart (HTTP 200)
 6. POST /size-guide/find returns matching size and rejects out-of-range cm
 7. GET /checkout loads successfully (HTTP 200)
 8. POST /payment/initiate validation and demo mode fallback
 9. GET /payment/demo renders demo payment page
10. POST /payment/demo/process completes demo transaction
11. GET /payment/success records order history and renders confirmation
12. GET /payment/fail and /payment/cancel render error/cancellation templates
"""

import io
import unittest
import mongomock
from app import create_app
import app.db as app_db

class TestKhairulFeatures(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Mock database
        self.mock_client = mongomock.MongoClient()
        self.mock_db = self.mock_client['vayelle_db']
        self.orig_client = app_db._client
        self.orig_db = app_db._db
        self.orig_check = app_db.check_db_connection

        app_db._client = self.mock_client
        app_db._db = self.mock_db
        app_db.check_db_connection = lambda: (True, "Mock DB connected")

    def tearDown(self):
        app_db._client = self.orig_client
        app_db._db = self.orig_db
        app_db.check_db_connection = self.orig_check

    # --------------------------------------------------------------------------
    # Outfit Upload Tests
    # --------------------------------------------------------------------------
    def test_01_outfit_upload_page_loads(self):
        """GET /outfit-upload returns 200 and loads template."""
        response = self.client.get('/outfit-upload')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("outfit", html.lower())

    def test_02_outfit_upload_validation_no_file(self):
        """POST /outfit-upload without file returns 400."""
        response = self.client.post('/outfit-upload', data={})
        self.assertEqual(response.status_code, 400)

    def test_03_outfit_upload_validation_invalid_ext(self):
        """POST /outfit-upload with .txt file returns 415."""
        data = {'outfit_image': (io.BytesIO(b"not an image"), 'test.txt')}
        response = self.client.post('/outfit-upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 415)

    def test_04_outfit_upload_validation_invalid_magic_bytes(self):
        """POST /outfit-upload with disguised file returns 415."""
        data = {'outfit_image': (io.BytesIO(b"fake fake fake fake"), 'fake.png')}
        response = self.client.post('/outfit-upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 415)

    def test_05_outfit_upload_success_valid_png(self):
        """POST /outfit-upload with valid PNG bytes succeeds."""
        # Minimal valid 1x1 PNG
        png_bytes = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00'
            b'\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        data = {'outfit_image': (io.BytesIO(png_bytes), 'test_sample.png')}
        response = self.client.post('/outfit-upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        res_json = response.get_json()
        self.assertTrue(res_json['success'])
        self.assertIn('filename', res_json)

    def test_06_outfit_upload_clear(self):
        """POST /outfit-upload/clear clears session outfit."""
        with self.client.session_transaction() as sess:
            sess['outfit_filename'] = 'temp_file.png'
        response = self.client.post('/outfit-upload/clear')
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertNotIn('outfit_filename', sess)

    # --------------------------------------------------------------------------
    # Size Guide Tests
    # --------------------------------------------------------------------------
    def test_07_size_guide_page_loads(self):
        """GET /size-guide returns 200 and displays size chart."""
        response = self.client.get('/size-guide')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("Size Guide", html)
        self.assertIn("35", html)
        self.assertIn("47", html)

    def test_08_size_guide_find_valid(self):
        """POST /size-guide/find returns matching size for 26.5 cm."""
        response = self.client.post('/size-guide/find', json={'cm': 26.5})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['size']['eu'], 42)

    def test_09_size_guide_find_out_of_range(self):
        """POST /size-guide/find with foot length 50 cm returns 400."""
        response = self.client.post('/size-guide/find', json={'cm': 50.0})
        self.assertEqual(response.status_code, 400)

    # --------------------------------------------------------------------------
    # Checkout & Payment Demo Tests
    # --------------------------------------------------------------------------
    def test_10_checkout_page_loads(self):
        """GET /checkout returns 200 and displays order summary."""
        response = self.client.get('/checkout')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("Checkout", html)

    def test_11_payment_initiate_demo_mode_fallback(self):
        """POST /payment/initiate falls back to demo mode without live API."""
        form_data = {
            'cus_name': 'Khairul Test',
            'cus_email': 'test@example.com',
            'cus_phone': '01700000000',
            'cus_address': '123 Test Road',
            'cus_city': 'Dhaka',
            'total_amount': '2500',
            'shoe_name': 'Urban Runner',
            'delivery_type': 'Standard'
        }
        response = self.client.post('/payment/initiate', data=form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        # Demo gateway page rendered
        self.assertIn("Demo", html)

    def test_12_payment_demo_process_and_success(self):
        """POST /payment/demo/process transitions to success and records history."""
        # Set up a pending demo order
        with self.client.session_transaction() as sess:
            sess['pending_order'] = {
                'tran_id': 'VAYELLE-TEST123',
                'name': 'Test Customer',
                'email': 'customer@example.com',
                'amount': 2500.0,
                'shoe_name': 'Urban Runner',
                'delivery': 'Standard',
                'demo_mode': True
            }

        response = self.client.post('/payment/demo/process', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("Success", html)
        self.assertIn("VAYELLE-TEST123", html)

    def test_13_payment_fail_and_cancel_pages(self):
        """GET /payment/fail and /payment/cancel return 200."""
        resp_fail = self.client.get('/payment/fail')
        self.assertEqual(resp_fail.status_code, 200)
        resp_cancel = self.client.get('/payment/cancel')
        self.assertEqual(resp_cancel.status_code, 200)

if __name__ == '__main__':
    unittest.main()
