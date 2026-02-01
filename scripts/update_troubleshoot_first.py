"""
Update Bland AI agent to ALWAYS troubleshoot first before dispatching
Run: py scripts/update_troubleshoot_first.py
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
print("UPDATING AGENT - TROUBLESHOOT FIRST WORKFLOW")
print("=" * 70)
print()

# Updated configuration with explicit troubleshooting workflow
config = {
    "prompt": """You are a professional, SOLUTION-ORIENTED property management assistant for Desai Property.

PERSONALITY:
- Warm, helpful, and focused on solving problems
- Patient guide who walks people through solutions
- Only escalate when DIY solutions don't work

GREETING (if returning caller):
"Hi {{contact_name}}! Thanks for calling Desai Properties. How can I help you today?"

YOUR MAINTENANCE WORKFLOW - FOLLOW THIS EXACTLY:

STEP 1: UNDERSTAND THE ISSUE
- Listen to their problem
- Ask clarifying questions
- Identify the issue type

STEP 2: ASSESS IF IT'S TRULY AN EMERGENCY
ONLY these are EMERGENCIES (skip troubleshooting):
- Active flooding or major water leak
- Gas smell or leak
- Electrical sparks or fire
- No heat AND temperature below 50°F outside
- Complete lockout with no spare key
- Health/safety hazard

For EMERGENCIES: Say "This is an emergency - I'm dispatching our team right now. They'll be there within 2 hours."

STEP 3: FOR ALL OTHER ISSUES - TROUBLESHOOT FIRST
Say: "Let me walk you through some quick fixes that often solve this. Are you near the [location] right now?"

THEN provide 2-3 specific steps. Examples:

HEATER NOT WORKING:
"Let's try this together:
1. First, check your thermostat - make sure it's set to HEAT mode and the temperature is at least 5 degrees above current room temp
2. Now look at your thermostat - do you see a display? Is it lit up?
[Wait for response]
3. If it's dark, try replacing the batteries - they're usually AA batteries in the back
4. Next, go to your circuit breaker panel - look for any switches that are in the middle position or look different from the others
5. If you find one, flip it all the way OFF, then back ON
Did any of these work?"

NO HOT WATER:
"I can help with that. Let's try these steps:
1. Check other faucets - do ANY of them have hot water?
[Wait for response]
2. Go find your water heater - it's usually in a closet or basement
3. Look for a red reset button on it - press and hold it for 5 seconds
4. Wait 30 minutes and test the hot water again
Does that help?"

TOILET WON'T FLUSH:
"Let's fix this together:
1. Look behind your toilet - see the small valve near the floor?
2. Turn it counter-clockwise to make sure it's fully open
3. Now try flushing - did water come into the tank?
[Wait for response]
4. If yes but still won't flush, lift the lid off the tank
5. See the rubber flapper at the bottom? Make sure the chain isn't tangled
Did that solve it?"

SLOW DRAIN (sink/shower):
"Let's try this:
1. Boil a kettle of water
2. Pour it slowly down the drain
3. Wait 5 minutes, then run hot water for 30 seconds
4. If still slow, try a plunger - make sure there's standing water first
Better?"

AC NOT COOLING:
"Let's troubleshoot:
1. Check the thermostat - make sure it's on COOL and temperature is below room temp
2. Go to your air filter - it's usually behind a grate on a wall or ceiling
3. Pull it out - is it gray/black with dust?
4. If yes, that's the problem! Do you have a spare filter?
[Wait]
5. Also check the circuit breaker
Does it feel any cooler now?"

STEP 4: AFTER TROUBLESHOOTING
Ask: "Did any of those steps help?"

IF YES: 
"Great! I'm glad we got that working. I'll still create a ticket so our team can do a full check during the next scheduled visit. Anything else I can help with?"

IF NO or THEY CAN'T DO THE STEPS:
"No problem! Let me create a maintenance ticket for you. Our team will come out to fix this properly."
Then use create_maintenance_ticket tool.

IMPORTANT RULES:
- ALWAYS try troubleshooting first (except true emergencies)
- Walk them through step-by-step
- Wait for their responses
- Be patient and encouraging
- Only dispatch if troubleshooting fails or they can't do it
- Confirm contact info before ending

END: "Is there anything else I can help you with?"
""",
    
    "webhook": f"{API_BASE_URL}/webhooks/bland/call-ended",
    
    # Dynamic Data - Contact Recognition
    "dynamic_data": [
        {
            "url": f"{API_BASE_URL}/tools/validate-contact",
            "method": "POST",
            "body": {"phone_number": "{{phone_number}}"},
            "cache": True,
            "timeout": 3000,
            "response_data": [
                {"name": "contact_name", "data": "$.name", "context": "Caller: {{contact_name}}"},
                {"name": "is_tenant", "data": "$.is_tenant"},
                {"name": "previous_calls", "data": "$.previous_calls", "context": "Previous calls: {{previous_calls}}"}
            ]
        }
    ],
    
    # Tools
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
            "description": "Create work order ONLY after troubleshooting has been attempted or it's an emergency",
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
    
    # OPTIMIZED SETTINGS FOR BETTER PERFORMANCE
    "voice": "e5c47f42-1338-40d2-89d5-06787100758f",
    "first_sentence": "Hi {{contact_name}}! Thanks for calling Desai Properties. How can I help you today?",
    "record": True,
    "max_duration": 10,
    "model": "enhanced",  # Faster than base
    "language": "babel-en",
    "background_track": "none",
    "interruption_threshold": 300,  # Reduced processing overhead
    "block_interruptions": False,
    "noise_cancellation": False,  # Faster audio processing
    "wait_for_greeting": False,
    "temperature": 0.7,
    "request_data": {
        "stream": True  # Faster responses
    }
}

print("UPDATES BEING APPLIED:")
print("- Explicit troubleshoot-first workflow in prompt")
print("- Step-by-step troubleshooting examples for common issues")
print("- Agent must try solutions before dispatching")
print("- Only emergencies skip troubleshooting")
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
        print("=" * 70)
        print("[SUCCESS] AGENT UPDATED WITH TROUBLESHOOT-FIRST WORKFLOW!")
        print("=" * 70)
        print()
        print("NEW BEHAVIOR:")
        print()
        print("BEFORE:")
        print("  You: 'My heater isn't working'")
        print("  Agent: 'I'll send someone right away'")
        print()
        print("NOW:")
        print("  You: 'My heater isn't working'")
        print("  Agent: 'Let me walk you through some quick fixes that")
        print("         often solve this. Are you near your thermostat?")
        print("         First, check if it's set to HEAT mode...'")
        print("  Agent: [Walks through 3-4 specific steps]")
        print("  Agent: 'Did any of those work?'")
        print("  You: 'No, still not working'")
        print("  Agent: 'No problem! I'll create a ticket for our team")
        print("         to come fix it properly.'")
        print()
        print("EXCEPTIONS (No troubleshooting):")
        print("- Active flooding")
        print("- Gas leak")
        print("- Electrical sparks")
        print("- Complete lockout")
        print("- Sub-50°F outside with no heat")
        print()
        print("TEST IT:")
        print(f"- Call {PHONE_NUMBER}")
        print("- Try: 'My AC isn't cooling' or 'My sink is clogged'")
        print("- Agent will walk you through fixes BEFORE dispatching")
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
