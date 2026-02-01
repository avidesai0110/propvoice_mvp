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
    "call_id": "test-inbound-call-123",
    "c_id": "test-inbound-call-123",
    "to": "+16307963284",  # Your inbound number
    "from": "+16309438357",  # Caller's number
    "call_length": 145,
    "duration": 145,
    "concatenated_transcript": "Agent: Thank you for calling Desai Property, this is your virtual assistant. How can I help you today? Caller: Hi, I'm interested in renting a 2 bedroom apartment. Agent: Great! Let me check our available units for you. I found several 2 bedroom units available. Would you like to schedule a tour?",
    "transcript": "Agent: Thank you for calling Desai Property, this is your virtual assistant. How can I help you today? Caller: Hi, I'm interested in renting a 2 bedroom apartment. Agent: Great! Let me check our available units for you. I found several 2 bedroom units available. Would you like to schedule a tour?",
    "recording_url": "https://example.com/recording-inbound.mp3",
    "created_at": "2026-01-31T18:50:00Z",
    "completed_at": "2026-01-31T18:52:25Z",
    "inbound": True,
    "direction": "inbound",
    "answered": True,
    "queue_status": "completed",
    "endpoint_url": "https://acerbic-madalynn-nonthoracic.ngrok-free.dev",
    "max_duration": 10,
    "error_message": None,
    "variables": {
        "inquiry_type": "leasing",
        "bedrooms_requested": "2"
    }
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
