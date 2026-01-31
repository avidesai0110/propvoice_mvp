"""
Test Supabase REST API insert directly (bypasses our app).
Run: py scripts/test_supabase_insert.py
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL", "").rstrip("/") + "/rest/v1/calls"
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("[ERROR] Set SUPABASE_URL and SUPABASE_KEY in .env")
    exit(1)

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

data = {
    "bland_call_id": "test-direct-insert-999",
    "from_number": "+16309438357",
    "to_number": "+15551234567",
    "duration": 60,
    "transcript": "Test transcript",
    "status": "completed",
}

print(f"POST {url}")
r = requests.post(url, headers=headers, json=data, timeout=10)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")

if r.ok:
    print("\n[OK] Insert succeeded! Check Supabase > calls table")
else:
    print("\n[FAIL] If 401/403: check your SUPABASE_KEY (use anon key)")
    print("If 404: check SUPABASE_URL")
    print("If RLS error: may need to use service_role key or fix RLS policies")
