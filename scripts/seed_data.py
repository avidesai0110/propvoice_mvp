"""
Seed Database with Test Data
Run this after creating your Supabase schema to add test property and units

Uses Supabase REST API directly (via requests) to avoid supabase-py client compatibility issues.

Usage:
    py scripts/seed_data.py
"""
import os
import sys
import json
from dotenv import load_dotenv
import requests

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
PROPERTY_NAME = os.getenv("PROPERTY_NAME", "Sunset Apartments")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERROR] SUPABASE_URL and SUPABASE_KEY must be set in .env")
    sys.exit(1)

# Supabase REST API base URL
REST_URL = f"{SUPABASE_URL.rstrip('/')}/rest/v1"

# Headers for Supabase REST API
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# Test property data
PROPERTY_DATA = {
    "name": PROPERTY_NAME,
    "address": "123 Main Street",
    "city": "Jacksonville",
    "state": "FL",
    "zip_code": "32201",
    "phone": "+19045551234",
    "email": "info@sunsetapts.com",
    "manager_name": "Property Manager",
    "manager_email": os.getenv("MANAGER_EMAIL", "manager@sunsetapts.com"),
}

# Test units data
UNITS_DATA = [
    {
        "unit_number": "101",
        "bedrooms": 1,
        "bathrooms": 1.0,
        "square_feet": 650,
        "rent": 1250.00,
        "deposit": 1250.00,
        "status": "available",
        "amenities": ["Washer/Dryer In-Unit", "Balcony", "Updated Kitchen"],
        "description": "Cozy 1BR with private balcony overlooking the courtyard",
    },
    {
        "unit_number": "102",
        "bedrooms": 1,
        "bathrooms": 1.0,
        "square_feet": 700,
        "rent": 1350.00,
        "deposit": 1350.00,
        "status": "available",
        "amenities": ["Washer/Dryer In-Unit", "Walk-in Closet", "Stainless Appliances"],
        "description": "Recently renovated 1BR with modern finishes",
    },
    {
        "unit_number": "201",
        "bedrooms": 2,
        "bathrooms": 1.0,
        "square_feet": 900,
        "rent": 1650.00,
        "deposit": 1650.00,
        "status": "available",
        "amenities": ["Washer/Dryer In-Unit", "Balcony", "Walk-in Closet", "Dishwasher"],
        "description": "Spacious 2BR corner unit with extra windows",
    },
    {
        "unit_number": "202",
        "bedrooms": 2,
        "bathrooms": 2.0,
        "square_feet": 1000,
        "rent": 1850.00,
        "deposit": 1850.00,
        "status": "occupied",
        "amenities": ["Washer/Dryer In-Unit", "Balcony", "2 Full Baths", "Stainless Appliances"],
        "description": "Premium 2BR/2BA with en-suite master bathroom",
    },
    {
        "unit_number": "301",
        "bedrooms": 3,
        "bathrooms": 2.0,
        "square_feet": 1200,
        "rent": 2250.00,
        "deposit": 2250.00,
        "status": "available",
        "amenities": ["Washer/Dryer In-Unit", "Balcony", "Walk-in Closet", "City Views", "Office Nook"],
        "description": "Top floor 3BR with stunning city views",
    },
    {
        "unit_number": "302",
        "bedrooms": 3,
        "bathrooms": 2.0,
        "square_feet": 1300,
        "rent": 2450.00,
        "deposit": 2450.00,
        "status": "maintenance",
        "amenities": ["Washer/Dryer In-Unit", "Large Balcony", "Den", "City Views", "Premium Finishes"],
        "description": "Penthouse 3BR with wrap-around views - being renovated",
    },
    {
        "unit_number": "103",
        "bedrooms": 1,
        "bathrooms": 1.0,
        "square_feet": 600,
        "rent": 1150.00,
        "deposit": 1150.00,
        "status": "available",
        "amenities": ["Washer/Dryer In-Unit", "Patio"],
        "description": "Ground floor 1BR with private patio - pet friendly!",
    },
    {
        "unit_number": "203",
        "bedrooms": 2,
        "bathrooms": 1.0,
        "square_feet": 850,
        "rent": 1550.00,
        "deposit": 1550.00,
        "status": "available",
        "amenities": ["Washer/Dryer In-Unit", "Updated Kitchen", "Ceiling Fans"],
        "description": "Well-maintained 2BR in quiet location",
    },
]


def supabase_get(table: str, params: dict | None = None) -> list:
    """GET request to Supabase REST API"""
    url = f"{REST_URL}/{table}"
    r = requests.get(url, headers=HEADERS, params=params or {}, timeout=30)
    r.raise_for_status()
    return r.json() if r.text else []


def supabase_post(table: str, data: dict | list) -> list:
    """POST (insert) request to Supabase REST API"""
    url = f"{REST_URL}/{table}"
    r = requests.post(url, headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json() if r.text else []


def seed_database():
    """Seed the database with test data"""
    try:
        print("""
============================================================
              Seeding Database with Test Data
============================================================
""")

        # Check if property already exists
        existing = supabase_get("properties", {"name": f"eq.{PROPERTY_NAME}"})

        if existing:
            print(f"[SKIP] Property '{PROPERTY_NAME}' already exists.")
            property_id = existing[0]["id"]
        else:
            # Create property
            print(f"Creating property: {PROPERTY_NAME}...")
            result = supabase_post("properties", PROPERTY_DATA)
            property_id = result[0]["id"]
            print(f"[OK] Property created with ID: {property_id}")

        # Get existing units for this property
        existing_units = supabase_get(
            "units",
            {"property_id": f"eq.{property_id}", "select": "unit_number"},
        )
        existing_unit_numbers = {u["unit_number"] for u in existing_units}

        # Add units
        units_added = 0
        for unit in UNITS_DATA:
            if unit["unit_number"] in existing_unit_numbers:
                print(f"  [SKIP] Unit {unit['unit_number']} already exists")
                continue

            unit_data = {**unit, "property_id": property_id}
            supabase_post("units", unit_data)
            print(f"  [OK] Added unit {unit['unit_number']} - {unit['bedrooms']}BR ${unit['rent']}/mo")
            units_added += 1

        # Show available units
        available = supabase_get(
            "units",
            {
                "property_id": f"eq.{property_id}",
                "status": "eq.available",
                "select": "unit_number,bedrooms,rent,status",
                "order": "rent.asc",
            },
        )

        print(f"""
============================================================
                    Seeding Complete!
============================================================

  Property: {PROPERTY_NAME}
  Units Added: {units_added}

  Available Units:""")

        for unit in available:
            print(f"    Unit {unit['unit_number']}: {unit['bedrooms']}BR - ${unit['rent']:,.0f}/mo")

        print("""
============================================================
""")

    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP error: {e}")
        if e.response is not None:
            try:
                detail = e.response.json()
                print(f"        {json.dumps(detail, indent=2)}")
            except Exception:
                print(f"        {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Error seeding database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    seed_database()
