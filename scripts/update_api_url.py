"""
Helper script to update .env with a new API_BASE_URL
Run: py scripts/update_api_url.py <NEW_URL>
Example: py scripts/update_api_url.py https://propvoice.loca.lt
"""
import sys
import os

if len(sys.argv) < 2:
    print("Usage: py scripts/update_api_url.py <NEW_URL>")
    print()
    print("Example:")
    print("  py scripts/update_api_url.py https://propvoice.loca.lt")
    sys.exit(1)

new_url = sys.argv[1].rstrip('/')
env_file = ".env"

if not os.path.exists(env_file):
    print(f"Error: {env_file} not found")
    sys.exit(1)

# Read .env
with open(env_file, 'r') as f:
    lines = f.readlines()

# Update API_BASE_URL
updated = False
for i, line in enumerate(lines):
    if line.startswith('API_BASE_URL='):
        old_url = line.split('=', 1)[1].strip()
        lines[i] = f'API_BASE_URL={new_url}\n'
        updated = True
        print(f"Updated API_BASE_URL:")
        print(f"  Old: {old_url}")
        print(f"  New: {new_url}")
        break

if not updated:
    print("Error: API_BASE_URL not found in .env")
    sys.exit(1)

# Write back
with open(env_file, 'w') as f:
    f.writelines(lines)

print()
print("[SUCCESS] .env updated!")
print()
print("Next steps:")
print("1. Restart your FastAPI server (Ctrl+C and rerun)")
print("2. Run: py scripts/update_inbound_webhook.py")
print("3. Make a test call to +16307963284")
print("4. Check server logs for incoming webhook")
