"""
Test the full webhook flow including email (Supabase + OpenAI + Resend).
Run: py scripts/test_email.py

Requires: Server running (py -m uvicorn app.main:app --host 0.0.0.0 --port 8000)
"""
import requests
import json

WEBHOOK_URL = "http://localhost:8000/webhooks/bland/call-ended"

# Sample call with transcript - triggers: save -> AI summary -> email
data = {
    "call_id": "test-email-flow-001",
    "from": "+16309438357",
    "to": "+15551234567",
    "call_length": 145,
    "concatenated_transcript": (
        "Agent: Thank you for calling Desai Property. How can I help you today? "
        "Caller: Hi, I'm interested in a 2 bedroom apartment. Agent: Great! What's your budget? "
        "Caller: Around 1700 a month. Agent: I found Unit 201 at 1650 and Unit 203 at 1550. "
        "Caller: I'd like to schedule a tour for Saturday afternoon. Agent: Perfect. Can I get your "
        "name and email? Caller: Jane Smith, jane@example.com. Agent: I've scheduled your tour. "
        "You'll receive a confirmation email shortly. Thank you for calling!"
    ),
    "recording_url": "https://example.com/recording.mp3",
    "created_at": "2025-01-30T21:00:00Z",
}

print("Testing full flow (Supabase + OpenAI + Resend)...")
print(f"POST {WEBHOOK_URL}\n")

r = requests.post(WEBHOOK_URL, json=data, timeout=60)
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")

if r.status_code == 200:
    result = r.json()
    if result.get("status") == "success":
        print("\n[OK] Full flow completed!")
        print("  - Call saved to Supabase")
        print("  - AI summary generated")
        print("  - Email sent to MANAGER_EMAIL")
        print("\nCheck your inbox at avidesai0110@gmail.com (or your MANAGER_EMAIL)")
    else:
        print(f"\n[FAIL] {result.get('message', 'Unknown error')}")
else:
    print("\n[FAIL] Webhook returned error. Check server logs.")
