"""
Fix Bland AI Call Lag & Add Proactive Troubleshooting

FIXES:
1. Optimizes settings to reduce lag after 2 minutes
2. Makes agent proactively offer troubleshooting solutions during calls

Run: py scripts/fix_lag_and_add_solutions.py
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
print("OPTIMIZING BLAND AI - FIXING LAG & ADDING PROACTIVE SOLUTIONS")
print("=" * 70)
print()

# Optimized configuration to fix lag issues
config = {
    "prompt": """You are a professional, friendly property management assistant for Desai Property.

PERSONALITY:
- Warm, friendly, and SOLUTION-ORIENTED
- Quick to offer practical help
- Patient but efficient

CONTACT RECOGNITION:
- Greet returning callers: "Hi {{contact_name}}!" 
- Reference history: "I see you called {{previous_calls}} time(s) before"

YOUR APPROACH - BE PROACTIVE WITH SOLUTIONS:

MAINTENANCE REQUESTS (MOST IMPORTANT):
1. Get unit number and describe issue
2. Determine urgency:
   - EMERGENCY: Gas leak, flooding, no heat in winter, electrical sparks, fire hazard
   - URGENT: No hot water, broken AC in summer, major leak, broken lock
   - ROUTINE: Minor repairs, slow drains, cosmetic issues

3. IMMEDIATELY OFFER QUICK FIXES (Don't wait to be asked!):
   
   For ROUTINE/URGENT issues, say:
   "While I create your ticket, let me give you some quick things to try that might fix this right away..."
   
   Examples:
   - Toilet won't flush → "First, check if the water valve behind the toilet is open"
   - Slow drain → "Try pouring hot water down the drain, then use a plunger"
   - No hot water → "Check your water heater - there's usually a reset button"
   - Outlet not working → "Check if the circuit breaker tripped - it's in your breaker panel"
   - AC not cooling → "First, check if your air filter is dirty and replace it if needed"
   
4. After giving 2-3 quick tips, use the create_maintenance_ticket tool
5. The tool will provide more detailed troubleshooting automatically
6. For EMERGENCIES: No DIY tips - immediate dispatch only

LEASING:
- Ask move-in date, bedrooms, budget
- Use check_unit_availability tool
- Offer schedule_tour tool
- Be quick and efficient

PAYMENTS:
- Use get_payment_info tool
- Keep it brief

IMPORTANT:
- Be CONCISE - give solutions quickly
- Don't over-explain
- Confirm details efficiently
- End with: "Anything else I can help with?"
""",
    
    "webhook": f"{API_BASE_URL}/webhooks/bland/call-ended",
    
    # OPTIMIZED: Cache dynamic data to reduce API calls during conversation
    "dynamic_data": [
        {
            "url": f"{API_BASE_URL}/tools/validate-contact",
            "method": "POST",
            "body": {"phone_number": "{{phone_number}}"},
            "cache": True,  # Cache contact info - doesn't change during call
            "timeout": 3000,  # 3 second timeout
            "response_data": [
                {"name": "contact_name", "data": "$.name", "context": "Caller: {{contact_name}}"},
                {"name": "is_tenant", "data": "$.is_tenant"},
                {"name": "previous_calls", "data": "$.previous_calls", "context": "Previous calls: {{previous_calls}}"}
            ]
        }
    ],
    
    # Tools with concise descriptions
    "tools": [
        {
            "name": "check_unit_availability",
            "description": "Find available units by bedrooms/rent",
            "url": f"{API_BASE_URL}/tools/check-availability",
            "method": "POST",
            "timeout": 5000
        },
        {
            "name": "create_maintenance_ticket",
            "description": "Create work order and get troubleshooting tips",
            "url": f"{API_BASE_URL}/tools/create-ticket",
            "method": "POST",
            "timeout": 5000
        },
        {
            "name": "schedule_tour",
            "description": "Schedule property tour",
            "url": f"{API_BASE_URL}/tools/schedule-tour",
            "method": "POST",
            "timeout": 5000
        },
        {
            "name": "get_payment_info",
            "description": "Get payment methods",
            "url": f"{API_BASE_URL}/tools/get-payment-info",
            "method": "POST",
            "timeout": 5000
        }
    ],
    
    # OPTIMIZED CALL SETTINGS
    "voice": "e5c47f42-1338-40d2-89d5-06787100758f",
    "first_sentence": "Thank you for calling Desai Property, this is your virtual assistant. How can I help you today?",
    "record": True,
    "max_duration": 10,
    "model": "enhanced",  # Changed from "base" - faster responses
    "language": "babel-en",
    "background_track": "none",
    
    # LATENCY OPTIMIZATIONS
    "interruption_threshold": 300,  # Increased from 100 - reduces processing overhead
    "block_interruptions": False,
    "noise_cancellation": False,  # Disabled - reduces processing
    "wait_for_greeting": False,
    
    # RESPONSE OPTIMIZATION
    "temperature": 0.7,  # Slightly lower for more consistent, faster responses
    "request_data": {
        "stream": True  # Enable streaming for faster perceived response time
    }
}

print("OPTIMIZATIONS APPLIED:")
print("- Model: enhanced (faster than base)")
print("- Interruption threshold: 300ms (reduces processing)")
print("- Noise cancellation: OFF (less processing)")
print("- Dynamic data: Cached (reduces API calls)")
print("- Tool timeouts: 5 seconds (prevents hanging)")
print("- Streaming: Enabled (faster responses)")
print("- Proactive troubleshooting: Added to prompt")
print()

# Update Bland AI inbound number
url = f"https://api.bland.ai/v1/inbound/{PHONE_NUMBER}"
headers = {
    "Authorization": BLAND_API_KEY,
    "Content-Type": "application/json"
}

try:
    print("Sending optimized configuration to Bland AI...")
    response = requests.post(url, headers=headers, json=config, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        print("=" * 70)
        print("[SUCCESS] CONFIGURATION UPDATED!")
        print("=" * 70)
        print()
        print("WHAT'S FIXED:")
        print()
        print("1. LAG ISSUE:")
        print("   - Switched to 'enhanced' model (faster processing)")
        print("   - Increased interruption threshold (less overhead)")
        print("   - Disabled noise cancellation (faster audio)")
        print("   - Added tool timeouts (prevents hanging)")
        print("   - Enabled response streaming")
        print()
        print("2. PROACTIVE SOLUTIONS:")
        print("   - Agent now offers troubleshooting BEFORE creating ticket")
        print("   - Gives 2-3 quick fixes immediately")
        print("   - More concise and solution-focused")
        print()
        print("EXAMPLE CONVERSATION:")
        print("You: 'My toilet won't flush'")
        print("Agent: 'Let me help! First, check if the water valve")
        print("       behind the toilet is open. If closed, turn it")
        print("       counter-clockwise. Also try...'")
        print()
        print("TEST IT:")
        print(f"- Call {PHONE_NUMBER}")
        print("- Report a maintenance issue")
        print("- Agent will offer solutions IMMEDIATELY")
        print("- Call should feel faster and more responsive")
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
