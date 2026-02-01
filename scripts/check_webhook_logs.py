"""
Research: Test if webhook is actually being called by Bland
This checks recent server logs for any incoming webhook attempts
"""
import os
import sys
from datetime import datetime, timedelta

# Path to the server terminal log
LOG_FILE = r"C:\Users\avide\.cursor\projects\c-Users-avide-Desktop-propvoice-mvp\terminals\180744.txt"

print("Checking server logs for webhook activity...")
print("=" * 60)

try:
    with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Look for webhook-related lines
    lines = content.split('\n')
    webhook_lines = []
    
    for i, line in enumerate(lines):
        if any(keyword in line.lower() for keyword in ['webhook', 'call ended', 'call_id', '/webhooks/']):
            webhook_lines.append(f"Line {i+1}: {line}")
    
    if webhook_lines:
        print("Found webhook activity:")
        print()
        for line in webhook_lines[-20:]:  # Last 20 webhook-related lines
            print(line)
    else:
        print("No webhook activity found in server logs.")
        print()
        print("This means either:")
        print("1. No calls have been made to your inbound number yet")
        print("2. Bland AI is not sending webhooks to your server")
        print("3. The webhook URL is not reachable from Bland's servers")
    
    print()
    print("=" * 60)
    
except FileNotFoundError:
    print(f"Server log not found at: {LOG_FILE}")
    print("Is the server running?")
except Exception as e:
    print(f"Error reading log: {e}")

print()
print("To test if webhooks would work:")
print("1. Make sure ngrok is running (check http://127.0.0.1:4040)")
print("2. Make sure your server is running on port 8000")
print("3. Call your Bland number: +16307963284")
print("4. Watch this log file for incoming webhook POST requests")
