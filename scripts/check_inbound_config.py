"""
Check current inbound number configuration on Bland AI
Run: py scripts/check_inbound_config.py
"""
import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

BLAND_API_KEY = os.getenv("BLAND_API_KEY")
PHONE_NUMBER = "+16307963284"

if not BLAND_API_KEY:
    print("ERROR: BLAND_API_KEY not found in .env")
    sys.exit(1)

print(f"Checking inbound configuration for: {PHONE_NUMBER}")
print(f"API Key: {BLAND_API_KEY[:20]}...")
print()

# Get current configuration
url = f"https://api.bland.ai/v1/inbound/{PHONE_NUMBER}"
headers = {
    "Authorization": BLAND_API_KEY,
    "Content-Type": "application/json"
}

try:
    response = requests.get(url, headers=headers, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        config = response.json()
        print("Current Configuration:")
        print("=" * 60)
        print(json.dumps(config, indent=2))
        print("=" * 60)
        print()
        
        # Check webhook specifically
        webhook = config.get("webhook")
        if webhook:
            print(f"✅ Webhook configured: {webhook}")
        else:
            print("❌ No webhook configured!")
            print()
            print("The webhook field is missing. Bland won't send call data to your server.")
            
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
