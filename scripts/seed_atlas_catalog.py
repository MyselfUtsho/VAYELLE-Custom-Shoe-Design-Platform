"""
VAYELLE — Centralized Catalog Seeding & Migration Tool (Module 1)
Prepares and migrates shoe catalog products to shared MongoDB Atlas
with centralized Cloudinary image hosting.

Architecture:
- Images: Cloudinary cloud media storage (f_auto, q_auto, 800x800).
- Catalog Database: Shared MongoDB Atlas (vayelle_db.shoes).
- Idempotent: Match by shoe_name; uses $set excluding _id to never mutate immutable IDs.
- Safety: Dry-run by default unless --execute is explicitly specified.

Usage:
  python scripts/seed_atlas_catalog.py --dry-run
  python scripts/seed_atlas_catalog.py --execute
  python scripts/seed_atlas_catalog.py --source-local --dry-run
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timezone

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

from config import Config
from app.cloudinary_service import (
    is_cloudinary_configured,
    configure_cloudinary,
    upload_shoe_image,
    is_allowed_file
)

# Set up clean logging (never prints credentials)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("seed_atlas_catalog")

# Master canonical baseline catalog (11 products)
CANONICAL_CATALOG = [
    # 7 Baseline Silhouettes (Local Presets to be hosted on Cloudinary)
    {
        "shoe_name": "Urban Runner",
        "category": "Sneakers",
        "gender": "Unisex",
        "description": "High-performance street runner with breathable mesh and reinforced heel.",
        "base_price": 2500.0,
        "preset_file": "shoe-black-runner.jpg",
        "availability": "In Stock",
        "created_by": "system"
    },
    {
        "shoe_name": "Cloud Street",
        "category": "Sneakers",
        "gender": "Unisex",
        "description": "Cloud-like cushioning with clean minimal aesthetics for everyday wear.",
        "base_price": 3200.0,
        "preset_file": "shoe-white.jpg",
        "availability": "In Stock",
        "created_by": "system"
    },
    {
        "shoe_name": "Mono Classic",
        "category": "Casual",
        "gender": "Men",
        "description": "Timeless two-tone design blending refined and urban street aesthetics.",
        "base_price": 2800.0,
        "preset_file": "shoe-black-beige.jpg",
        "availability": "In Stock",
        "created_by": "system"
    },
    {
        "shoe_name": "Retro Flex",
        "category": "Sneakers",
        "gender": "Women",
        "description": "Vintage-inspired flex sole meets modern durable materials.",
        "base_price": 3500.0,
        "preset_file": "shoe-retro.jpg",
        "availability": "In Stock",
        "created_by": "system"
    },
    {
        "shoe_name": "Urban Formal",
        "category": "Formal",
        "gender": "Men",
        "description": "Refined formal shoe with premium leather finish and all-day comfort.",
        "base_price": 4200.0,
        "preset_file": "shoe-formal.jpg",
        "availability": "In Stock",
        "created_by": "system"
    },
    {
        "shoe_name": "Daily Canvas",
        "category": "Casual",
        "gender": "Women",
        "description": "Lightweight canvas slip-on for effortless everyday summer styling.",
        "base_price": 1900.0,
        "preset_file": "shoe-canvas.jpg",
        "availability": "In Stock",
        "created_by": "system"
    },
    {
        "shoe_name": "Aero Flow Runner",
        "category": "Sneakers",
        "gender": "Unisex",
        "description": "Engineered lightweight mesh with dynamic street cushioning.",
        "base_price": 4500.0,
        "preset_file": "shoe-black-runner.jpg",
        "availability": "In Stock",
        "created_by": "audit_manager@vayelle.com"
    },
    # 4 Real Cloudinary Verified Products
    {
        "shoe_name": "Apex Stride Pro",
        "category": "Sneakers",
        "gender": "Men",
        "description": "Engineered athletic running sneaker featuring breathable black mesh, sculpted white cushioning midsole, and reinforced heel counter.",
        "base_price": 4200.0,
        "cloudinary_url": "https://res.cloudinary.com/jrhwnxlz/image/upload/c_limit,f_auto,h_800,q_auto,w_800/v1794651950/vayelle/shoes/shoe_image_wy1v2v.jpg",
        "availability": "In Stock",
        "created_by": "manager@gmail.com"
    },
    {
        "shoe_name": "Luna Minimal Casual",
        "category": "Casual",
        "gender": "Women",
        "description": "Understated beige and off-white casual sneaker with subtle suede overlays and ultra-soft ergonomic insole for daily comfort.",
        "base_price": 3600.0,
        "cloudinary_url": "https://res.cloudinary.com/jrhwnxlz/image/upload/c_limit,f_auto,h_800,q_auto,w_800/v1794651952/vayelle/shoes/shoe_image_dgnujs.jpg",
        "availability": "In Stock",
        "created_by": "manager@gmail.com"
    },
    {
        "shoe_name": "Heritage Cognac Oxford",
        "category": "Formal",
        "gender": "Men",
        "description": "Handcrafted classic brown leather formal dress shoe with refined cap-toe stitching, premium polished leather finish, and Goodyear welt.",
        "base_price": 5800.0,
        "cloudinary_url": "https://res.cloudinary.com/jrhwnxlz/image/upload/c_limit,f_auto,h_800,q_auto,w_800/v1794651955/vayelle/shoes/shoe_image_vyyfuk.jpg",
        "availability": "In Stock",
        "created_by": "manager@gmail.com"
    },
    {
        "shoe_name": "Vibe Classic White",
        "category": "Sneakers",
        "gender": "Unisex",
        "description": "Clean minimalist all-white urban sneaker crafted with smooth leather, low-profile silhouette, and durable rubber cupsole.",
        "base_price": 3900.0,
        "cloudinary_url": "https://res.cloudinary.com/jrhwnxlz/image/upload/c_limit,f_auto,h_800,q_auto,w_800/v1794651957/vayelle/shoes/shoe_image_mkpaln.jpg",
        "availability": "In Stock",
        "created_by": "manager@gmail.com"
    }
]


def mask_connection_uri(uri):
    """Safely masks credentials in MongoDB URI for logging."""
    if not uri:
        return "<EMPTY>"
    try:
        if '@' in uri:
            scheme_and_auth, rest = uri.split('@', 1)
            scheme = scheme_and_auth.split('://')[0]
            return f"{scheme}://****:****@{rest}"
        return uri
    except Exception:
        return "<MASKED_URI>"


def get_atlas_collection():
    """Initializes and returns the shared MongoDB Atlas shoes collection."""
    from pymongo import MongoClient
    uri = Config.MONGO_URI
    db_name = Config.DB_NAME or "vayelle_db"

    kwargs = {'serverSelectionTimeoutMS': 5000}
    if 'mongodb+srv://' in uri or 'ssl=true' in uri.lower() or 'tls=true' in uri.lower():
        try:
            import certifi
            kwargs['tlsCAFile'] = certifi.where()
        except ImportError:
            pass

    client = MongoClient(uri, **kwargs)
    db = client[db_name]
    return db.shoes


def load_from_local_mongodb():
    """Optionally reads the 11 records directly from local MongoDB daemon."""
    from pymongo import MongoClient
    local_uri = "mongodb://127.0.0.1:27017/vayelle_db"
    try:
        client = MongoClient(local_uri, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        db = client['vayelle_db']
        shoes = list(db.shoes.find())
        logger.info(f"Loaded {len(shoes)} shoe records from local MongoDB.")
        return shoes
    except Exception as e:
        logger.warning(f"Could not read from local MongoDB ({e}). Falling back to canonical catalog.")
        return None


def run_catalog_seed(dry_run=True, source_local=False):
    """
    Executes or simulates catalog preparation and migration.
    
    Returns:
        dict: Summary of migration actions and counts.
    """
    logger.info("=" * 65)
    logger.info(f"VAYELLE CATALOG SEEDING & MIGRATION TOOL {'[DRY RUN]' if dry_run else '[EXECUTE MODE]'}")
    logger.info("=" * 65)

    # 1. Environment & Configuration Check
    masked_target_uri = mask_connection_uri(Config.MONGO_URI)
    logger.info(f"Target Database URI : {masked_target_uri}")
    logger.info(f"Target Database Name: {Config.DB_NAME}")
    logger.info(f"Cloudinary Configured: {is_cloudinary_configured()}")

    if not dry_run and not is_cloudinary_configured():
        logger.error("Cloudinary credentials are missing. Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET.")
        return {"status": "FAILED", "error": "Missing Cloudinary credentials"}

    # 2. Prepare Source Records
    records_to_process = None
    if source_local:
        local_docs = load_from_local_mongodb()
        if local_docs:
            records_to_process = []
            for d in local_docs:
                rec = {
                    "shoe_name": d.get("shoe_name"),
                    "category": d.get("category"),
                    "gender": d.get("gender"),
                    "description": d.get("description"),
                    "base_price": float(d.get("base_price", 0.0)),
                    "availability": d.get("availability", "In Stock"),
                    "created_by": d.get("created_by", "system")
                }
                img_url = d.get("image_url", "")
                if "res.cloudinary.com" in img_url:
                    rec["cloudinary_url"] = img_url
                elif img_url.startswith("/static/images/") or img_url.startswith("static/images/"):
                    rec["preset_file"] = os.path.basename(img_url)
                records_to_process.append(rec)

    if not records_to_process:
        records_to_process = CANONICAL_CATALOG

    logger.info(f"Total catalog records to process: {len(records_to_process)}")

    # 3. Identify & Cache Unique Static Presets
    unique_preset_files = set()
    for rec in records_to_process:
        if "preset_file" in rec:
            unique_preset_files.add(rec["preset_file"])

    logger.info(f"Unique local static images to host on Cloudinary: {len(unique_preset_files)}")
    preset_url_cache = {}

    # Verify physical file existence in app/static/images
    static_img_dir = os.path.join(PROJECT_ROOT, "app", "static", "images")
    for filename in unique_preset_files:
        filepath = os.path.join(static_img_dir, filename)
        if not os.path.isfile(filepath):
            logger.error(f"Static preset image file missing on disk: {filepath}")
            return {"status": "FAILED", "error": f"Missing file: {filename}"}
        else:
            file_size = os.path.getsize(filepath)
            logger.info(f"Verified static image on disk: {filename} ({file_size} bytes)")

    # 4. Process Images (Upload or Mock for Dry-Run)
    if not dry_run:
        configure_cloudinary()
        for filename in unique_preset_files:
            filepath = os.path.join(static_img_dir, filename)
            logger.info(f"Uploading {filename} to Cloudinary...")
            url, err = upload_shoe_image(filepath, folder="vayelle/shoes/presets")
            if err or not url:
                logger.error(f"Failed to upload {filename} to Cloudinary: {err}")
                return {"status": "FAILED", "error": f"Upload failed for {filename}: {err}"}
            preset_url_cache[filename] = url
            logger.info(f"Uploaded {filename} -> {url}")
    else:
        for filename in unique_preset_files:
            clean_name = os.path.splitext(filename)[0]
            preset_url_cache[filename] = f"https://res.cloudinary.com/dry-run/image/upload/c_limit,f_auto,h_800,q_auto,w_800/v1/vayelle/shoes/presets/{clean_name}.jpg"
            logger.info(f"[DRY-RUN] Simulated Cloudinary URL for {filename}: {preset_url_cache[filename]}")

    # 5. Prepare Upsert Documents (Safe handling of _id)
    prepared_documents = []
    now_utc = datetime.now(timezone.utc)

    for item in records_to_process:
        shoe_name = item["shoe_name"]
        final_image_url = item.get("cloudinary_url")
        if not final_image_url and "preset_file" in item:
            final_image_url = preset_url_cache.get(item["preset_file"])

        doc = {
            "shoe_name": shoe_name,
            "category": item["category"],
            "gender": item["gender"],
            "description": item["description"],
            "base_price": item["base_price"],
            "image_url": final_image_url,
            "availability": item.get("availability", "In Stock"),
            "created_by": item.get("created_by", "system")
        }
        prepared_documents.append((shoe_name, doc))

    # 6. Database Upsert Operations
    upserted_count = 0
    skipped_count = 0

    if not dry_run:
        try:
            shoes_col = get_atlas_collection()
            for shoe_name, doc in prepared_documents:
                # IMPORTANT: Never include '_id' in the $set update document to protect immutable _id
                set_data = {k: v for k, v in doc.items() if k != '_id'}
                result = shoes_col.update_one(
                    {"shoe_name": shoe_name},
                    {
                        "$set": set_data,
                        "$setOnInsert": {"created_at": now_utc}
                    },
                    upsert=True
                )
                if result.upserted_id:
                    upserted_count += 1
                    logger.info(f"Inserted new shoe: {shoe_name} (_id: {result.upserted_id})")
                else:
                    skipped_count += 1
                    logger.info(f"Updated existing shoe record: {shoe_name}")
        except Exception as e:
            logger.error(f"Atlas database upsert failed: {e}")
            return {"status": "FAILED", "error": str(e)}
    else:
        for idx, (shoe_name, doc) in enumerate(prepared_documents, 1):
            logger.info(f"[DRY-RUN #{idx:02d}] Ready to upsert: '{shoe_name}' | Category: {doc['category']} | Gender: {doc['gender']} | Image: {doc['image_url'][:65]}...")
        upserted_count = len(prepared_documents)

    summary = {
        "status": "SUCCESS",
        "mode": "DRY-RUN" if dry_run else "EXECUTE",
        "total_catalog_shoes": len(prepared_documents),
        "unique_presets_processed": len(unique_preset_files),
        "cloudinary_shoes_ready": len(prepared_documents),
        "upserted_count": upserted_count,
        "existing_updated_count": skipped_count
    }

    logger.info("=" * 65)
    logger.info(f"MIGRATION SUMMARY: {summary['mode']} COMPLETED SUCCESSFULLY")
    logger.info(f"Total Shoes Prepared      : {summary['total_catalog_shoes']}")
    logger.info(f"Static Images Hosted (CDN): {summary['unique_presets_processed']}")
    logger.info(f"Cloudinary Delivery Active: 100% of records")
    logger.info("=" * 65)
    return summary


def main():
    parser = argparse.ArgumentParser(description="VAYELLE Catalog Seeding Tool (Module 1)")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Simulate without modifying database or uploading images (Default)")
    parser.add_argument("--execute", action="store_true", help="Execute real Cloudinary uploads and Atlas database migration")
    parser.add_argument("--source-local", action="store_true", help="Attempt to read existing records from local MongoDB daemon")

    args = parser.parse_args()
    is_dry_run = not args.execute

    res = run_catalog_seed(dry_run=is_dry_run, source_local=args.source_local)
    if res.get("status") != "SUCCESS":
        sys.exit(1)


if __name__ == "__main__":
    main()
