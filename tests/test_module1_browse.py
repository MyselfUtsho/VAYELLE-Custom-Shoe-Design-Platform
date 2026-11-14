"""
VAYELLE — Module 1 Automated Test Suite: Browse Shoes by Category
Author: Athoy Roy (ID: 23101197)
Tests:
1. Explore page route loads with HTTP 200
2. Shoes retrieved dynamically from MongoDB
3. Product card fields verified (name, price, category, gender, description)
4. Gender filtering (Men, Women, Unisex, All)
5. Shoe type / category filtering (Sneakers, Casual, Formal, All)
6. Combined gender and category filtering
7. Filter reset restores full catalog
8. Empty search results display friendly empty state
9. Cloudinary / image URL rendering with onerror fallback
10. Graceful error handling when database is unavailable
11. Legacy /category route redirection to /explore
"""

import unittest
from datetime import datetime, timezone
import mongomock
from app import create_app
import app.db as app_db

class TestBrowseShoesByCategory(unittest.TestCase):
    
    def setUp(self):
        # Create Flask app in test mode
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Setup mock MongoDB client
        self.mock_client = mongomock.MongoClient()
        self.mock_db = self.mock_client['vayelle_db']
        
        # Override the global DB client in app.db
        app_db._client = self.mock_client
        app_db._db = self.mock_db
        
        # Seed test shoes in mock database
        self.sample_shoes = [
            {
                "shoe_name": "Urban Runner",
                "category": "Sneakers",
                "gender": "Unisex",
                "description": "High-performance street runner.",
                "base_price": 2500.0,
                "image_url": "https://res.cloudinary.com/vayelle/image/upload/v1/shoes/urban-runner.jpg",
                "availability": "In Stock",
                "created_at": datetime.now(timezone.utc)
            },
            {
                "shoe_name": "Cloud Street",
                "category": "Sneakers",
                "gender": "Unisex",
                "description": "Cloud-like cushioning for everyday.",
                "base_price": 3200.0,
                "image_url": "https://res.cloudinary.com/vayelle/image/upload/v1/shoes/cloud-street.jpg",
                "availability": "In Stock",
                "created_at": datetime.now(timezone.utc)
            },
            {
                "shoe_name": "Mono Classic",
                "category": "Casual",
                "gender": "Men",
                "description": "Timeless two-tone urban design.",
                "base_price": 2800.0,
                "image_url": "/static/images/shoe-black-beige.jpg",
                "availability": "In Stock",
                "created_at": datetime.now(timezone.utc)
            },
            {
                "shoe_name": "Retro Flex",
                "category": "Sneakers",
                "gender": "Women",
                "description": "Vintage-inspired flex sole.",
                "base_price": 3500.0,
                "image_url": "https://res.cloudinary.com/vayelle/image/upload/v1/shoes/retro-flex.jpg",
                "availability": "In Stock",
                "created_at": datetime.now(timezone.utc)
            },
            {
                "shoe_name": "Urban Formal",
                "category": "Formal",
                "gender": "Men",
                "description": "Refined formal shoe with leather finish.",
                "base_price": 4200.0,
                "image_url": "/static/images/shoe-formal.jpg",
                "availability": "In Stock",
                "created_at": datetime.now(timezone.utc)
            },
            {
                "shoe_name": "Daily Canvas",
                "category": "Casual",
                "gender": "Women",
                "description": "Lightweight canvas slip-on.",
                "base_price": 1900.0,
                "image_url": "/static/images/shoe-canvas.jpg",
                "availability": "In Stock",
                "created_at": datetime.now(timezone.utc)
            }
        ]
        self.mock_db.shoes.insert_many(self.sample_shoes)
        
    def tearDown(self):
        app_db._client = None
        app_db._db = None

    def test_01_explore_page_loads_successfully(self):
        """Verify the /explore route returns HTTP 200 and loads HTML template."""
        response = self.client.get('/explore')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Browse Shoes by Category", response.data)
        self.assertIn(b"Explore Shoes", response.data)

    def test_02_all_shoes_displayed_by_default(self):
        """Verify all 6 shoes from MongoDB are displayed when no filters applied."""
        response = self.client.get('/explore')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Showing <strong style=\"color:var(--text-heading);\">6</strong> shoes", response.data)
        self.assertIn(b"Urban Runner", response.data)
        self.assertIn(b"Cloud Street", response.data)
        self.assertIn(b"Mono Classic", response.data)
        self.assertIn(b"Retro Flex", response.data)
        self.assertIn(b"Urban Formal", response.data)
        self.assertIn(b"Daily Canvas", response.data)

    def test_03_product_card_fields_present(self):
        """Verify shoe cards display name, price, category, gender, and image."""
        response = self.client.get('/explore')
        # Check prices formatted with currency
        self.assertIn(b"2,500", response.data)
        self.assertIn(b"4,200", response.data)
        # Check categories
        self.assertIn(b"Sneakers", response.data)
        self.assertIn(b"Formal", response.data)
        # Check gender badges
        self.assertIn(b"Men", response.data)
        self.assertIn(b"Women", response.data)
        self.assertIn(b"Unisex", response.data)

    def test_04_gender_filtering_men(self):
        """Verify filtering by gender=Men returns only Men's shoes (Mono Classic, Urban Formal)."""
        response = self.client.get('/explore?gender=Men')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Showing <strong style=\"color:var(--text-heading);\">2</strong> shoes", response.data)
        self.assertIn(b"Mono Classic", response.data)
        self.assertIn(b"Urban Formal", response.data)
        # Women and Unisex shoes should not appear
        self.assertNotIn(b"Retro Flex", response.data)
        self.assertNotIn(b"Daily Canvas", response.data)
        self.assertNotIn(b"Urban Runner", response.data)

    def test_05_gender_filtering_women(self):
        """Verify filtering by gender=Women returns only Women's shoes (Retro Flex, Daily Canvas)."""
        response = self.client.get('/explore?gender=Women')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Showing <strong style=\"color:var(--text-heading);\">2</strong> shoes", response.data)
        self.assertIn(b"Retro Flex", response.data)
        self.assertIn(b"Daily Canvas", response.data)
        self.assertNotIn(b"Mono Classic", response.data)
        self.assertNotIn(b"Urban Formal", response.data)

    def test_06_gender_filtering_unisex(self):
        """Verify filtering by gender=Unisex returns only Unisex shoes (Urban Runner, Cloud Street)."""
        response = self.client.get('/explore?gender=Unisex')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Showing <strong style=\"color:var(--text-heading);\">2</strong> shoes", response.data)
        self.assertIn(b"Urban Runner", response.data)
        self.assertIn(b"Cloud Street", response.data)
        self.assertNotIn(b"Mono Classic", response.data)

    def test_07_category_filtering_sneakers(self):
        """Verify filtering by category=Sneakers returns all sneakers."""
        response = self.client.get('/explore?category=Sneakers')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Showing <strong style=\"color:var(--text-heading);\">3</strong> shoes", response.data)
        self.assertIn(b"Urban Runner", response.data)
        self.assertIn(b"Cloud Street", response.data)
        self.assertIn(b"Retro Flex", response.data)
        self.assertNotIn(b"Urban Formal", response.data)
        self.assertNotIn(b"Daily Canvas", response.data)

    def test_08_category_filtering_formal(self):
        """Verify filtering by category=Formal returns only formal shoes."""
        response = self.client.get('/explore?category=Formal')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Showing <strong style=\"color:var(--text-heading);\">1</strong> shoe", response.data)
        self.assertIn(b"Urban Formal", response.data)
        self.assertNotIn(b"Urban Runner", response.data)

    def test_09_combined_filtering_men_and_casual(self):
        """Verify combined filter (gender=Men AND category=Casual) returns Mono Classic."""
        response = self.client.get('/explore?gender=Men&category=Casual')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Showing <strong style=\"color:var(--text-heading);\">1</strong> shoe", response.data)
        self.assertIn(b"Mono Classic", response.data)
        self.assertNotIn(b"Urban Formal", response.data)  # Formal, not Casual

    def test_10_combined_filtering_women_and_sneakers(self):
        """Verify combined filter (gender=Women AND category=Sneakers) returns Retro Flex."""
        response = self.client.get('/explore?gender=Women&category=Sneakers')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Showing <strong style=\"color:var(--text-heading);\">1</strong> shoe", response.data)
        self.assertIn(b"Retro Flex", response.data)
        self.assertNotIn(b"Daily Canvas", response.data)  # Casual, not Sneakers

    def test_11_empty_results_handled_gracefully(self):
        """Verify when no shoes match (e.g. Men + Sneakers), empty state is rendered."""
        response = self.client.get('/explore?gender=Men&category=Sneakers')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No Shoes Found", response.data)
        self.assertIn(b"Browse All Shoes", response.data)

    def test_12_reset_filters_restores_catalog(self):
        """Verify navigating to /explore?gender=All&category=All restores all 6 shoes."""
        response = self.client.get('/explore?gender=All&category=All')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Showing <strong style=\"color:var(--text-heading);\">6</strong> shoes", response.data)

    def test_13_cloudinary_image_url_rendered(self):
        """Verify Cloudinary URLs and fallback onerror attributes are rendered."""
        response = self.client.get('/explore')
        self.assertIn(b"https://res.cloudinary.com/vayelle/image/upload/v1/shoes/urban-runner.jpg", response.data)
        self.assertIn(b"onerror=\"this.src='/static/images/shoe-black-runner.jpg'\"", response.data)

    def test_14_legacy_category_route_redirects(self):
        """Verify /category?cat=men redirects to /explore?gender=Men."""
        response = self.client.get('/category?cat=men')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/explore?gender=Men', response.headers.get('Location'))

        response2 = self.client.get('/category?cat=sneakers')
        self.assertEqual(response2.status_code, 302)
        self.assertIn('/explore?category=Sneakers', response2.headers.get('Location'))


if __name__ == '__main__':
    unittest.main()
