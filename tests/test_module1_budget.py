"""
VAYELLE — Module 1 Automated Test Suite: Budget-Based Shoe Search
Author: Diya Zerin (ID: 22101062)

Test Cases:
 1. /budget loads successfully (HTTP 200)
 2. Minimum-only search (min_price specified)
 3. Maximum-only search (max_price specified)
 4. Minimum and maximum together (range search)
 5. Minimum equal to maximum (exact price search)
 6. Empty search submission (empty parameters)
 7. Negative minimum price rejected with friendly error message
 8. Negative maximum price rejected with friendly error message
 9. Non-numeric input rejected with friendly error message
10. Minimum greater than maximum rejected with friendly error message
11. No matching products displays friendly empty state
12. MongoDB connection failure handled gracefully without crashing
13. Correct ascending price sorting (lowest to highest)
14. Correct product image and product details displayed
15. Quick budget range links present and functional
16. Clear search functionality restores default state
"""

import unittest
from datetime import datetime, timezone
import mongomock
from app import create_app
import app.db as app_db

class TestBudgetBasedShoeSearch(unittest.TestCase):
    
    def setUp(self):
        # Create Flask app in test mode
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Setup mock MongoDB client
        self.mock_client = mongomock.MongoClient()
        self.mock_db = self.mock_client['vayelle_db']
        
        # Override the global DB client in app.db
        self.orig_client = app_db._client
        self.orig_db = app_db._db
        self.orig_check = app_db.check_db_connection
        
        app_db._client = self.mock_client
        app_db._db = self.mock_db
        app_db.check_db_connection = lambda: (True, "Mock MongoDB connected successfully.")
        
        # Seed test shoes in mock database (with varied prices)
        self.sample_shoes = [
            {
                "shoe_name": "Daily Canvas",
                "category": "Casual",
                "gender": "Women",
                "description": "Lightweight canvas slip-on for effortless everyday summer styling.",
                "base_price": 1900.0,
                "image_url": "/static/images/shoe-canvas.jpg",
                "availability": "In Stock",
                "created_at": datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc)
            },
            {
                "shoe_name": "Urban Runner",
                "category": "Sneakers",
                "gender": "Unisex",
                "description": "High-performance street runner with breathable mesh.",
                "base_price": 2500.0,
                "image_url": "/static/images/shoe-black-runner.jpg",
                "availability": "In Stock",
                "created_at": datetime(2026, 11, 2, 10, 0, tzinfo=timezone.utc)
            },
            {
                "shoe_name": "Mono Classic",
                "category": "Casual",
                "gender": "Men",
                "description": "Timeless two-tone design blending refined and urban street aesthetics.",
                "base_price": 2800.0,
                "image_url": "/static/images/shoe-black-beige.jpg",
                "availability": "In Stock",
                "created_at": datetime(2026, 11, 3, 10, 0, tzinfo=timezone.utc)
            },
            {
                "shoe_name": "Cloud Street",
                "category": "Sneakers",
                "gender": "Unisex",
                "description": "Cloud-like cushioning with clean minimal aesthetics for everyday wear.",
                "base_price": 3200.0,
                "image_url": "/static/images/shoe-white.jpg",
                "availability": "In Stock",
                "created_at": datetime(2026, 11, 4, 10, 0, tzinfo=timezone.utc)
            },
            {
                "shoe_name": "Retro Flex",
                "category": "Sneakers",
                "gender": "Women",
                "description": "Vintage-inspired flex sole meets modern durable materials.",
                "base_price": 3500.0,
                "image_url": "/static/images/shoe-retro.jpg",
                "availability": "In Stock",
                "created_at": datetime(2026, 11, 5, 10, 0, tzinfo=timezone.utc)
            },
            {
                "shoe_name": "Urban Formal",
                "category": "Formal",
                "gender": "Men",
                "description": "Refined formal shoe with premium leather finish and all-day comfort.",
                "base_price": 4200.0,
                "image_url": "/static/images/shoe-formal.jpg",
                "availability": "In Stock",
                "created_at": datetime(2026, 11, 6, 10, 0, tzinfo=timezone.utc)
            }
        ]
        self.mock_db.shoes.insert_many(self.sample_shoes)

    def tearDown(self):
        app_db._client = self.orig_client
        app_db._db = self.orig_db
        app_db.check_db_connection = self.orig_check

    # --------------------------------------------------------------------------
    # Test 1: Page Loads Successfully
    # --------------------------------------------------------------------------
    def test_01_budget_page_loads_successfully(self):
        """1. Verify /budget loads with HTTP 200 and renders the budget template."""
        response = self.client.get('/budget')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("Budget-Based Shoe Search", html)
        self.assertIn("Set Your Budget Range", html)
        self.assertIn('name="min_price"', html)
        self.assertIn('name="max_price"', html)

    # --------------------------------------------------------------------------
    # Test 2: Minimum-only Search
    # --------------------------------------------------------------------------
    def test_02_minimum_only_search(self):
        """2. Verify minimum-only search returns shoes >= min_price."""
        response = self.client.get('/budget?min_price=3000')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        # Should include: Cloud Street (3200), Retro Flex (3500), Urban Formal (4200)
        self.assertIn("Cloud Street", html)
        self.assertIn("Retro Flex", html)
        self.assertIn("Urban Formal", html)
        # Should NOT include: Daily Canvas (1900), Urban Runner (2500), Mono Classic (2800)
        self.assertNotIn("Daily Canvas", html)
        self.assertNotIn("Urban Runner", html)
        self.assertNotIn("Mono Classic", html)
        self.assertIn("Found", html)

    # --------------------------------------------------------------------------
    # Test 3: Maximum-only Search
    # --------------------------------------------------------------------------
    def test_03_maximum_only_search(self):
        """3. Verify maximum-only search returns shoes <= max_price."""
        response = self.client.get('/budget?max_price=2600')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        # Should include: Daily Canvas (1900), Urban Runner (2500)
        self.assertIn("Daily Canvas", html)
        self.assertIn("Urban Runner", html)
        # Should NOT include: Mono Classic (2800), Cloud Street (3200), Retro Flex (3500), Urban Formal (4200)
        self.assertNotIn("Mono Classic", html)
        self.assertNotIn("Cloud Street", html)
        self.assertNotIn("Urban Formal", html)

    # --------------------------------------------------------------------------
    # Test 4: Minimum and Maximum Together
    # --------------------------------------------------------------------------
    def test_04_minimum_and_maximum_together(self):
        """4. Verify range search between min_price and max_price."""
        response = self.client.get('/budget?min_price=2500&max_price=3500')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        # Should include: Urban Runner (2500), Mono Classic (2800), Cloud Street (3200), Retro Flex (3500)
        self.assertIn("Urban Runner", html)
        self.assertIn("Mono Classic", html)
        self.assertIn("Cloud Street", html)
        self.assertIn("Retro Flex", html)
        # Excluded: Daily Canvas (1900), Urban Formal (4200)
        self.assertNotIn("Daily Canvas", html)
        self.assertNotIn("Urban Formal", html)

    # --------------------------------------------------------------------------
    # Test 5: Minimum Equal to Maximum
    # --------------------------------------------------------------------------
    def test_05_minimum_equal_to_maximum(self):
        """5. Verify exact budget match when min_price equals max_price."""
        response = self.client.get('/budget?min_price=2500&max_price=2500')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("Urban Runner", html)
        self.assertNotIn("Daily Canvas", html)
        self.assertNotIn("Cloud Street", html)

    # --------------------------------------------------------------------------
    # Test 6: Empty Search Submission
    # --------------------------------------------------------------------------
    def test_06_empty_search_submission(self):
        """6. Verify empty search submission renders prompt without crashing."""
        response = self.client.get('/budget?min_price=&max_price=')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("Set Your Budget Range", html)

    # --------------------------------------------------------------------------
    # Test 7: Negative Minimum Price
    # --------------------------------------------------------------------------
    def test_07_negative_minimum_price(self):
        """7. Verify negative minimum price is rejected with a validation error."""
        response = self.client.get('/budget?min_price=-500&max_price=3000')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("Minimum price cannot be negative", html)

    # --------------------------------------------------------------------------
    # Test 8: Negative Maximum Price
    # --------------------------------------------------------------------------
    def test_08_negative_maximum_price(self):
        """8. Verify negative maximum price is rejected with a validation error."""
        response = self.client.get('/budget?min_price=1000&max_price=-100')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("Maximum price cannot be negative", html)

    # --------------------------------------------------------------------------
    # Test 9: Non-Numeric Input
    # --------------------------------------------------------------------------
    def test_09_non_numeric_input(self):
        """9. Verify non-numeric input is safely caught and displays validation error."""
        response = self.client.get('/budget?min_price=abc&max_price=xyz')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("must be a valid number", html)

    # --------------------------------------------------------------------------
    # Test 10: Minimum Greater Than Maximum
    # --------------------------------------------------------------------------
    def test_10_minimum_greater_than_maximum(self):
        """10. Verify min_price > max_price displays error message."""
        response = self.client.get('/budget?min_price=5000&max_price=2000')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("Minimum price cannot be greater than maximum price", html)

    # --------------------------------------------------------------------------
    # Test 11: No Matching Products
    # --------------------------------------------------------------------------
    def test_11_no_matching_products(self):
        """11. Verify friendly empty state when no shoes match the range."""
        response = self.client.get('/budget?min_price=50000&max_price=60000')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("No Shoes Found in This Budget", html)

    # --------------------------------------------------------------------------
    # Test 12: MongoDB Connection Failure Graceful Handling
    # --------------------------------------------------------------------------
    def test_12_mongodb_connection_failure(self):
        """12. Verify app handles database connection failure gracefully without HTTP 500."""
        app_db.check_db_connection = lambda: (False, "Simulated database connection timeout")
        response = self.client.get('/budget?min_price=1000&max_price=5000')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("Budget-Based Shoe Search", html)
        self.assertIn("No Shoes Found in This Budget", html)

    # --------------------------------------------------------------------------
    # Test 13: Correct Ascending Price Sorting
    # --------------------------------------------------------------------------
    def test_13_ascending_price_sorting(self):
        """13. Verify shoes are returned in ascending order of base_price."""
        response = self.client.get('/budget?min_price=1000&max_price=5000')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        
        # Check that Daily Canvas (1900) appears before Urban Runner (2500)
        pos_daily = html.find("Daily Canvas")
        pos_runner = html.find("Urban Runner")
        pos_mono = html.find("Mono Classic")
        pos_cloud = html.find("Cloud Street")
        pos_retro = html.find("Retro Flex")
        pos_formal = html.find("Urban Formal")
        
        self.assertTrue(pos_daily < pos_runner < pos_mono < pos_cloud < pos_retro < pos_formal)

    # --------------------------------------------------------------------------
    # Test 14: Product Image and Details Rendered
    # --------------------------------------------------------------------------
    def test_14_product_details_rendered(self):
        """14. Verify product card displays image, name, category, gender, and BDT formatted price."""
        response = self.client.get('/budget?min_price=2000&max_price=3000')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn("Urban Runner", html)
        self.assertIn("Sneakers", html)
        self.assertIn("Unisex", html)
        self.assertIn("৳2,500", html)
        self.assertIn("/static/images/shoe-black-runner.jpg", html)

    # --------------------------------------------------------------------------
    # Test 15: Quick Budget Range Links
    # --------------------------------------------------------------------------
    def test_15_quick_budget_range_links(self):
        """15. Verify quick budget range filter chips are present in the HTML."""
        response = self.client.get('/budget')
        html = response.data.decode('utf-8')
        self.assertIn("Under ৳2,000", html)
        self.assertIn("৳2,000 – ৳4,000", html)
        self.assertIn("৳4,000 – ৳6,000", html)
        self.assertIn("৳6,000 – ৳10,000", html)
        self.assertIn("৳10,000+", html)

    # --------------------------------------------------------------------------
    # Test 16: Clear Search Functionality
    # --------------------------------------------------------------------------
    def test_16_clear_search_functionality(self):
        """16. Verify Clear button is shown when search is active and links to /budget."""
        response = self.client.get('/budget?min_price=2000&max_price=4000')
        html = response.data.decode('utf-8')
        self.assertIn("Clear", html)
        self.assertIn('href="/budget"', html)

if __name__ == '__main__':
    unittest.main()
