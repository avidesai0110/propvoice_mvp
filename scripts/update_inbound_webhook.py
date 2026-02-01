"""
Update inbound number configuration to ensure webhooks are sent
Run: py scripts/update_inbound_webhook.py
"""
import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

BLAND_API_KEY = os.getenv("BLAND_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL")
PHONE_NUMBER = "+16307963284"

if not BLAND_API_KEY or not API_BASE_URL:
    print("ERROR: Missing BLAND_API_KEY or API_BASE_URL in .env")
    sys.exit(1)

print(f"Updating inbound configuration for: {PHONE_NUMBER}")
print(f"Webhook URL: {API_BASE_URL}/webhooks/bland/call-ended")
print()

# Update configuration with webhook_events and tools
url = f"https://api.bland.ai/v1/inbound/{PHONE_NUMBER}"
headers = {
    "Authorization": BLAND_API_KEY,
    "Content-Type": "application/json"
}

# Full configuration with all fields
config = {
    "prompt": "You are a professional, friendly property management assistant for Desai Property.\n\nPERSONALITY:\n- Warm, friendly, and genuinely helpful\n- Professional but conversational\n- Patient and understanding\n- Clear communicator who confirms important details\n\nYOUR ROLE:\nYou handle inbound calls for the property, including:\n1) Leasing inquiries\n2) Maintenance requests\n3) Rent/payment questions\n4) General administrative questions\n\nLEASING:\n- Ask for desired move-in date, bedrooms, and budget.\n- Use the check_unit_availability tool to find available units.\n- Offer to schedule a tour using the schedule_tour tool.\n- Collect name, phone, and email for follow-up.\n\nMAINTENANCE:\n- Determine urgency (emergency/urgent/routine).\n- Collect unit number and a detailed description.\n- Use the create_maintenance_ticket tool to log the request.\n- If emergency, reassure caller and prioritize.\n\nPAYMENTS:\n- Use the get_payment_info tool to provide payment options.\n- Do NOT discuss sensitive account-specific balances.\n\nIMPORTANT RULES:\n- Confirm key details before taking actions.\n- If you cannot complete a request, offer a callback.\n\nEND:\nAsk if they need anything else, then thank them for calling Desai Property.\n",
    "webhook": f"{API_BASE_URL}/webhooks/bland/call-ended",
    "webhook_events": ["call.completed", "call.ended"],  # Enable webhook events
    "tools": [
        {
            "name": "check_unit_availability",
            "description": "Check available rental units by bedrooms and max rent",
            "url": f"{API_BASE_URL}/tools/check-availability",
            "method": "POST"
        },
        {
            "name": "create_maintenance_ticket",
            "description": "Create maintenance work order with unit number, issue type, description, urgency",
            "url": f"{API_BASE_URL}/tools/create-ticket",
            "method": "POST"
        },
        {
            "name": "schedule_tour",
            "description": "Schedule property tour with name, phone, email, date, time",
            "url": f"{API_BASE_URL}/tools/schedule-tour",
            "method": "POST"
        },
        {
            "name": "get_payment_info",
            "description": "Get payment methods and billing information",
            "url": f"{API_BASE_URL}/tools/get-payment-info",
            "method": "POST"
        }
    ],
    "voice": "e5c47f42-1338-40d2-89d5-06787100758f",
    "first_sentence": "Thank you for calling Desai Property, this is your virtual assistant. How can I help you today?",
    "record": True,
    "max_duration": 10,
    "model": "base",
    "language": "babel-en",
    "background_track": "none",
    "interruption_threshold": 100,
    "block_interruptions": False,
    "noise_cancellation": False
}

try:
    response = requests.post(url, headers=headers, json=config, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        print("Updated Configuration:")
        print("=" * 60)
        print(json.dumps(result, indent=2))
        print("=" * 60)
        print()
        print("[SUCCESS] Inbound number configuration updated!")
        print()
        print("Key changes:")
        print("- webhook_events: ['call.completed', 'call.ended']")
        print(f"- tools: Added {len(config['tools'])} tools")
        print()
        print("Next: Make a test call to your number and check:")
        print("1. Server logs for incoming webhook")
        print("2. Supabase 'calls' table for new record")
        print("3. Your email for call summary")
        
    else:
        print(f"[ERROR] {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
