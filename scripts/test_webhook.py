"""
Test webhook and Supabase integration directly.
Run: py scripts/test_webhook.py
"""
import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# Use localhost to avoid ngrok - server must be running
WEBHOOK_URL = "http://localhost:8000/webhooks/bland/call-ended"

test_data = {
    "call_id": "test-call-direct-789",
    "from": "+16309438357",
    "to": "+15551234567",
    "call_length": 120,
    "concatenated_transcript": "Agent: Thank you for calling Desai Property. Caller: I'm looking for a 2 bedroom. Agent: I found units for you.",
    "recording_url": "https://example.com/recording.mp3",
    "created_at": "2025-01-30T20:00:00Z",
}

print(f"Testing webhook: {WEBHOOK_URL}")
print(f"Data: {json.dumps(test_data, indent=2)}")
print()

r = requests.post(WEBHOOK_URL, json=test_data, timeout=30)
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")

if r.status_code == 200:
    try:
        data = r.json()
        if data.get("status") == "success":
            print(f"\n[OK] Call saved with ID: {data.get('call_id')}")
            print("Check Supabase Table Editor > calls")
        else:
            print(f"\n[FAIL] {data.get('message', r.text)}")
    except Exception:
        pass
else:
    print("\n[FAIL] Webhook returned error")
