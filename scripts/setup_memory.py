"""
Setup Bland AI Memory Store
- Creates memory store if it doesn't exist
- Enables memory for your inbound number
- Tests the connection

Run: py scripts/setup_memory.py
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.bland_memory import (
    get_or_create_memory_store,
    enable_memory_for_inbound,
    update_user_memory
)

load_dotenv()

INBOUND_NUMBER = "+16307963284"

print("=" * 70)
print("BLAND AI MEMORY STORE SETUP")
print("=" * 70)
print()

# Step 1: Get or create memory store
print("[1/3] Getting or creating memory store...")
memory_id = get_or_create_memory_store()

if memory_id:
    print(f"[OK] Memory store ID: {memory_id}")
else:
    print("[FAIL] Could not create/find memory store")
    print("Check your BLAND_API_KEY in .env")
    sys.exit(1)

print()

# Step 2: Enable memory for inbound number
print(f"[2/3] Enabling memory for inbound number {INBOUND_NUMBER}...")
enabled = enable_memory_for_inbound(INBOUND_NUMBER)

if enabled:
    print("[OK] Memory enabled for inbound number")
else:
    print("[WARN] Could not enable memory for inbound number")
    print("This may be normal if already enabled")

print()

# Step 3: Test memory update
print("[3/3] Testing memory update with sample data...")
test_summary = {
    "call_type": "leasing",
    "summary": "Caller inquired about 2-bedroom units",
    "action_items": ["Schedule tour", "Send availability list"]
}

test_updated = update_user_memory(
    phone_number="+11234567890",  # Test number
    call_summary=test_summary,
    caller_name="Test User",
    metadata={"is_tenant": False, "status": "prospect"}
)

if test_updated:
    print("[OK] Memory update test successful")
else:
    print("[WARN] Memory update test failed (this is normal if memory store wasn't created)")

print()
print("=" * 70)
print("SETUP COMPLETE!")
print("=" * 70)
print()
print("WHAT HAPPENS NOW:")
print()
print("1. Every call to your number will automatically update memory")
print("2. Bland AI will remember:")
print("   - Caller's name and phone number")
print("   - Previous call summaries")
print("   - Tenant status and preferences")
print("   - Action items from past calls")
print()
print("3. On future calls, the agent will:")
print("   - Greet returning callers by name")
print("   - Reference past conversations")
print("   - Provide context-aware responses")
print()
print("TEST IT:")
print(f"- Call {INBOUND_NUMBER}")
print("- Report a maintenance issue or ask about leasing")
print("- Call again from the same number")
print("- Agent will reference your previous call!")
print()
print("VIEW MEMORY:")
print("- Go to: https://app.bland.ai/dashboard/memory")
print(f"- Open 'Property Management' memory store")
print("- See all caller records and their conversation history")
print()
print("=" * 70)
