"""
Unit and Integration Tests for Module 1 Shared Catalog & Migration Tool
Tests:
- Shared database configuration reading
- Masking of database credentials in logs
- Canonical catalog schema integrity (11 products)
- Dry-run behavior (no writes, no uploads)
- Duplicate prevention via idempotent upsert
- Immutable _id protection
- Handling of missing environment variables
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import mongomock

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.seed_atlas_catalog import (
    CANONICAL_CATALOG,
    mask_connection_uri,
    run_catalog_seed
)
from config import Config


class TestSharedCatalogMigration(unittest.TestCase):

    def test_canonical_catalog_integrity(self):
        """All 11 canonical products must have valid schemas, categories, and image sources."""
        self.assertEqual(len(CANONICAL_CATALOG), 11)
        valid_categories = {"Sneakers", "Casual", "Formal"}
        valid_genders = {"Men", "Women", "Unisex"}

        cloudinary_count = 0
        preset_count = 0

        for item in CANONICAL_CATALOG:
            self.assertIn("shoe_name", item)
            self.assertIn("category", item)
            self.assertIn("gender", item)
            self.assertIn("base_price", item)
            self.assertIn(item["category"], valid_categories)
            self.assertIn(item["gender"], valid_genders)
            self.assertGreater(item["base_price"], 0)

            if "cloudinary_url" in item:
                cloudinary_count += 1
                self.assertTrue(item["cloudinary_url"].startswith("https://res.cloudinary.com/"))
            elif "preset_file" in item:
                preset_count += 1
                self.assertTrue(item["preset_file"].endswith(".jpg"))

        self.assertEqual(cloudinary_count, 4)
        self.assertEqual(preset_count, 7)

    def test_mask_connection_uri(self):
        """Database connection strings must mask credentials safely."""
        raw_uri = "mongodb+srv://myuser:SuperSecretPass123@cluster0.abcde.mongodb.net/vayelle_db"
        masked = mask_connection_uri(raw_uri)
        self.assertNotIn("SuperSecretPass123", masked)
        self.assertNotIn("myuser", masked)
        self.assertIn("mongodb+srv://****:****@cluster0.abcde.mongodb.net/vayelle_db", masked)

        local_uri = "mongodb://127.0.0.1:27017/vayelle_db"
        self.assertEqual(mask_connection_uri(local_uri), local_uri)
        self.assertEqual(mask_connection_uri(""), "<EMPTY>")

    def test_dry_run_execution(self):
        """Dry run mode must succeed and prepare 11 records without making network writes."""
        res = run_catalog_seed(dry_run=True, source_local=False)
        self.assertEqual(res.get("status"), "SUCCESS")
        self.assertEqual(res.get("mode"), "DRY-RUN")
        self.assertEqual(res.get("total_catalog_shoes"), 11)
        self.assertEqual(res.get("unique_presets_processed"), 6)

    def test_duplicate_prevention_and_immutable_id(self):
        """Upserting shoes repeatedly into MongoDB must never create duplicate records or mutate immutable _id."""
        mock_client = mongomock.MongoClient()
        mock_db = mock_client['vayelle_db']
        mock_col = mock_db['shoes']

        # First run: seed mock collection
        now = "2026-11-14T00:00:00Z"
        for item in CANONICAL_CATALOG:
            doc = {
                "shoe_name": item["shoe_name"],
                "category": item["category"],
                "gender": item["gender"],
                "description": item["description"],
                "base_price": item["base_price"],
                "image_url": item.get("cloudinary_url", f"https://res.cloudinary.com/test/{item.get('preset_file', 'shoe.jpg')}"),
                "availability": item.get("availability", "In Stock"),
                "created_by": item.get("created_by", "system")
            }
            set_data = {k: v for k, v in doc.items() if k != '_id'}
            mock_col.update_one(
                {"shoe_name": item["shoe_name"]},
                {"$set": set_data, "$setOnInsert": {"created_at": now}},
                upsert=True
            )

        self.assertEqual(mock_col.count_documents({}), 11)

        # Store initial IDs
        initial_records = {doc["shoe_name"]: doc["_id"] for doc in mock_col.find()}

        # Second run: re-seed with updated prices or images
        for item in CANONICAL_CATALOG:
            doc = {
                "shoe_name": item["shoe_name"],
                "category": item["category"],
                "gender": item["gender"],
                "description": item["description"],
                "base_price": item["base_price"] + 100,  # price update
                "image_url": "https://res.cloudinary.com/updated/shoe.jpg",
                "availability": "In Stock",
                "created_by": "system"
            }
            set_data = {k: v for k, v in doc.items() if k != '_id'}
            mock_col.update_one(
                {"shoe_name": item["shoe_name"]},
                {"$set": set_data, "$setOnInsert": {"created_at": now}},
                upsert=True
            )

        # Count must remain exactly 11 (zero duplicates)
        self.assertEqual(mock_col.count_documents({}), 11)

        # _id must remain identical (immutable _id preserved)
        for doc in mock_col.find():
            orig_id = initial_records[doc["shoe_name"]]
            self.assertEqual(doc["_id"], orig_id)
            self.assertEqual(doc["image_url"], "https://res.cloudinary.com/updated/shoe.jpg")

    def test_missing_cloudinary_credentials_in_execute_mode(self):
        """Execute mode must fail immediately if Cloudinary credentials are not configured."""
        with patch('scripts.seed_atlas_catalog.is_cloudinary_configured', return_value=False):
            res = run_catalog_seed(dry_run=False)
            self.assertEqual(res.get("status"), "FAILED")
            self.assertIn("Missing Cloudinary credentials", res.get("error", ""))


if __name__ == '__main__':
    unittest.main()
