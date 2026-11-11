"""
VAYELLE Management CLI
Used for administrative tasks such as initializing Manager accounts and database verification.
"""
import sys
import argparse
from datetime import datetime, timezone
from app.db import get_users_collection, get_shoes_collection, check_db_connection
from app.auth_utils import hash_password

def create_manager(name=None, email=None, password=None):
    """Creates or elevates a Manager account in MongoDB securely."""
    import getpass
    db_ok, msg = check_db_connection()
    if not db_ok:
        print(f"[ERROR] Could not connect to MongoDB: {msg}")
        sys.exit(1)

    users_col = get_users_collection()
    if users_col is None:
        print("[ERROR] Users collection unavailable.")
        sys.exit(1)

    while not name:
        name = input("Enter Manager Full Name: ").strip()
    while not email:
        email = input("Enter Manager Email: ").strip().lower()
    while not password:
        try:
            password = getpass.getpass("Enter Manager Password: ")
        except Exception:
            # Fallback if getpass fails in non-tty
            password = input("Enter Manager Password: ").strip()
        if len(password) < 6:
            print("[ERROR] Password must be at least 6 characters.")
            password = None
            continue
        try:
            confirm = getpass.getpass("Confirm Manager Password: ")
        except Exception:
            confirm = input("Confirm Manager Password: ").strip()
        if password != confirm:
            print("[ERROR] Passwords do not match. Please try again.")
            password = None

    email = email.strip().lower()
    existing = users_col.find_one({"email": email})

    pw_hash = hash_password(password)

    if existing:
        users_col.update_one(
            {"_id": existing["_id"]},
            {"$set": {
                "name": name,
                "password_hash": pw_hash,
                "role": "manager",
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        print(f"[SUCCESS] Existing user '{email}' elevated to MANAGER successfully.")
    else:
        new_manager = {
            "name": name,
            "email": email,
            "password_hash": pw_hash,
            "role": "manager",
            "created_at": datetime.now(timezone.utc)
        }
        users_col.insert_one(new_manager)
        print(f"[SUCCESS] Manager account created: Name: {name} | Email: {email} | Role: manager")

def test_database():
    """Tests the database connection and prints collections statistics."""
    print("Testing MongoDB connection...")
    db_ok, msg = check_db_connection()
    if db_ok:
        print(f"[SUCCESS] {msg}")
        users_col = get_users_collection()
        shoes_col = get_shoes_collection()
        user_count = users_col.count_documents({}) if users_col is not None else 0
        shoe_count = shoes_col.count_documents({}) if shoes_col is not None else 0
        print(f"Stats -> Users: {user_count} | Shoes in Inventory: {shoe_count}")
    else:
        print(f"[FAILURE] {msg}")

def seed_sample_shoes():
    """Seeds the 6 standard VAYELLE silhouettes into MongoDB (idempotent)."""
    db_ok, msg = check_db_connection()
    if not db_ok:
        print(f"[ERROR] Could not connect to MongoDB: {msg}")
        sys.exit(1)

    shoes_col = get_shoes_collection()
    if shoes_col is None:
        print("[ERROR] Shoes collection unavailable.")
        sys.exit(1)

    sample_shoes = [
        {
            "shoe_name": "Urban Runner",
            "category": "Sneakers",
            "gender": "Unisex",
            "description": "High-performance street runner with breathable mesh and reinforced heel.",
            "base_price": 2500.0,
            "image_url": "/static/images/shoe-black-runner.jpg",
            "availability": "In Stock",
            "created_at": datetime.now(timezone.utc),
            "created_by": "system"
        },
        {
            "shoe_name": "Cloud Street",
            "category": "Sneakers",
            "gender": "Unisex",
            "description": "Cloud-like cushioning with clean minimal aesthetics for everyday wear.",
            "base_price": 3200.0,
            "image_url": "/static/images/shoe-white.jpg",
            "availability": "In Stock",
            "created_at": datetime.now(timezone.utc),
            "created_by": "system"
        },
        {
            "shoe_name": "Mono Classic",
            "category": "Casual",
            "gender": "Men",
            "description": "Timeless two-tone design blending refined and urban street aesthetics.",
            "base_price": 2800.0,
            "image_url": "/static/images/shoe-black-beige.jpg",
            "availability": "In Stock",
            "created_at": datetime.now(timezone.utc),
            "created_by": "system"
        },
        {
            "shoe_name": "Retro Flex",
            "category": "Sneakers",
            "gender": "Women",
            "description": "Vintage-inspired flex sole meets modern durable materials.",
            "base_price": 3500.0,
            "image_url": "/static/images/shoe-retro.jpg",
            "availability": "In Stock",
            "created_at": datetime.now(timezone.utc),
            "created_by": "system"
        },
        {
            "shoe_name": "Urban Formal",
            "category": "Formal",
            "gender": "Men",
            "description": "Refined formal shoe with premium leather finish and all-day comfort.",
            "base_price": 4200.0,
            "image_url": "/static/images/shoe-formal.jpg",
            "availability": "In Stock",
            "created_at": datetime.now(timezone.utc),
            "created_by": "system"
        },
        {
            "shoe_name": "Daily Canvas",
            "category": "Casual",
            "gender": "Women",
            "description": "Lightweight canvas slip-on for effortless everyday summer styling.",
            "base_price": 1900.0,
            "image_url": "/static/images/shoe-canvas.jpg",
            "availability": "In Stock",
            "created_at": datetime.now(timezone.utc),
            "created_by": "system"
        }
    ]

    inserted = 0
    for s in sample_shoes:
        if not shoes_col.find_one({"shoe_name": s["shoe_name"]}):
            shoes_col.insert_one(s)
            inserted += 1

    print(f"[SUCCESS] Seeded {inserted} new shoe silhouettes into MongoDB (Total in inventory: {shoes_col.count_documents({})})")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="VAYELLE Management Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # create-manager
    mgr_parser = subparsers.add_parser("create-manager", help="Initialize or elevate a Manager user")
    mgr_parser.add_argument("--name", default=None, help="Manager full name")
    mgr_parser.add_argument("--email", default=None, help="Manager email address")
    mgr_parser.add_argument("--password", default=None, help="Manager password (omit to prompt interactively)")

    # test-db
    subparsers.add_parser("test-db", help="Verify MongoDB connectivity")

    # seed-shoes
    subparsers.add_parser("seed-shoes", help="Seed standard shoe catalog to MongoDB")

    args = parser.parse_args()

    if args.command == "create-manager":
        create_manager(args.name, args.email, args.password)
    elif args.command == "test-db":
        test_database()
    elif args.command == "seed-shoes":
        seed_sample_shoes()
    else:
        parser.print_help()
