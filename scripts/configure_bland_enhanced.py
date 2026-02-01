"""
Configure Bland AI inbound number with enhanced features:
- Contact recognition via Dynamic Data
- Troubleshooting tips tool
- Memory store integration
- All existing tools

Run: py scripts/configure_bland_enhanced.py
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

print("=" * 70)
print("CONFIGURING BLAND AI - ENHANCED PROPERTY VOICE AGENT")
print("=" * 70)
print(f"Phone Number: {PHONE_NUMBER}")
print(f"Webhook URL: {API_BASE_URL}/webhooks/bland/call-ended")
print()

# Enhanced configuration with all new features
config = {
    "prompt": """You are a professional, friendly property management assistant for Desai Property.

PERSONALITY:
- Warm, friendly, and genuinely helpful
- Professional but conversational
- Patient and understanding
- Remember returning callers and reference past conversations

YOUR ROLE:
You handle inbound calls for the property, including:
1) Leasing inquiries
2) Maintenance requests
3) Rent/payment questions
4) General administrative questions

CONTACT RECOGNITION:
- You have access to caller information via {{contact_name}} and {{is_tenant}} variables
- If the caller is a returning tenant, greet them by name: "Hi {{contact_name}}, thanks for calling!"
- Reference their history: "I see you've called {{previous_calls}} time(s) before"
- For new callers, introduce yourself warmly

LEASING INQUIRIES:
- Ask for desired move-in date, bedrooms, and budget
- Use the check_unit_availability tool to find available units
- Offer to schedule a tour using the schedule_tour tool
- Collect name, phone, and email for follow-up

MAINTENANCE REQUESTS:
- First, determine urgency:
  * EMERGENCY: Safety hazard, flooding, no heat in winter, gas leak, electrical sparks
  * URGENT: Issue affecting daily living (no hot water, broken AC in summer, etc.)
  * ROUTINE: Minor repairs, cosmetic issues
- Get unit number and detailed description
- Use the create_maintenance_ticket tool to log the request
- The tool will automatically provide troubleshooting tips for non-emergency issues
- For emergencies: Reassure caller that help is on the way immediately
- For urgent/routine: Mention the troubleshooting steps provided

PAYMENT QUESTIONS:
- Use the get_payment_info tool to provide payment options
- Do NOT discuss specific account balances
- Direct to resident portal or office for account-specific questions

IMPORTANT RULES:
- Confirm key details before taking actions
- Be empathetic, especially for maintenance emergencies
- If you cannot complete a request, offer a callback
- Use the caller's name when you have it

END EVERY CALL:
Ask "Is there anything else I can help you with?" then thank them for calling Desai Property.
""",
    
    "webhook": f"{API_BASE_URL}/webhooks/bland/call-ended",
    
    # Dynamic Data - Contact Recognition
    "dynamic_data": [
        {
            "url": f"{API_BASE_URL}/tools/validate-contact",
            "method": "POST",
            "body": {
                "phone_number": "{{phone_number}}"
            },
            "response_data": [
                {
                    "name": "contact_found",
                    "data": "$.contact_found"
                },
                {
                    "name": "contact_name",
                    "data": "$.name",
                    "context": "Caller's name: {{contact_name}}"
                },
                {
                    "name": "contact_email",
                    "data": "$.email"
                },
                {
                    "name": "is_tenant",
                    "data": "$.is_tenant",
                    "context": "This caller is a verified tenant: {{is_tenant}}"
                },
                {
                    "name": "previous_calls",
                    "data": "$.previous_calls",
                    "context": "Number of previous calls from this number: {{previous_calls}}"
                },
                {
                    "name": "contact_context",
                    "data": "$.context",
                    "context": "{{contact_context}}"
                }
            ]
        }
    ],
    
    # Tools - Including new troubleshooting endpoint
    "tools": [
        {
            "name": "check_unit_availability",
            "description": "Check available rental units by bedrooms and max rent",
            "url": f"{API_BASE_URL}/tools/check-availability",
            "method": "POST"
        },
        {
            "name": "create_maintenance_ticket",
            "description": "Create maintenance work order with unit number, issue type, description, urgency. Automatically provides troubleshooting tips.",
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
        },
        {
            "name": "get_troubleshooting_tips",
            "description": "Get detailed troubleshooting steps for maintenance issues (issue_type, description, urgency)",
            "url": f"{API_BASE_URL}/tools/get-troubleshooting-tips",
            "method": "POST"
        }
    ],
    
    # Voice and call settings
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

print("FEATURES ENABLED:")
print("[OK] Contact Recognition (Dynamic Data)")
print("[OK] Troubleshooting Tips (Automatic with tickets)")
print("[OK] Memory Store (Configure manually in Bland dashboard)")
print("[OK] 5 Custom Tools")
print()

# Update Bland AI inbound number
url = f"https://api.bland.ai/v1/inbound/{PHONE_NUMBER}"
headers = {
    "Authorization": BLAND_API_KEY,
    "Content-Type": "application/json"
}

try:
    print("Sending configuration to Bland AI...")
    response = requests.post(url, headers=headers, json=config, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        print("=" * 70)
        print("[SUCCESS] CONFIGURATION UPDATED!")
        print("=" * 70)
        print()
        print("NEXT STEPS:")
        print()
        print("1. SET UP MEMORY STORE (Optional but recommended):")
        print("   - Go to: https://app.bland.ai/dashboard/memory")
        print("   - Create new memory store: 'Property Management'")
        print("   - In inbound number settings, attach this memory store")
        print("   - This will help the agent remember past conversations")
        print()
        print("2. TEST THE AGENT:")
        print(f"   - Call {PHONE_NUMBER}")
        print("   - Try a maintenance request")
        print("   - Agent will:")
        print("     * Recognize if you're a returning caller")
        print("     * Provide troubleshooting tips automatically")
        print("     * Create ticket and send summary email")
        print()
        print("3. CHECK RESULTS:")
        print("   - Server logs for webhook activity")
        print("   - Supabase 'calls' table for call records")
        print("   - Email for call summary with troubleshooting tips")
        print()
        print("=" * 70)
        
    else:
        print(f"[ERROR] {response.status_code}")
        print(response.text)
        sys.exit(1)
        
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
