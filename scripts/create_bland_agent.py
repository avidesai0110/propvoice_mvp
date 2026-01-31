"""
Bland AI Agent Setup Script
Creates or updates the voice agent configuration in Bland AI

Run this script AFTER:
1. Setting up your environment variables (.env)
2. Deploying your API (or using ngrok for local testing)
3. Running the Supabase schema

Usage:
    python scripts/create_bland_agent.py
"""
import requests
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BLAND_API_KEY = os.getenv("BLAND_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
PROPERTY_NAME = os.getenv("PROPERTY_NAME", "Sunset Apartments")

if not BLAND_API_KEY:
    print("[ERROR] BLAND_API_KEY not found in environment variables")
    print("   Please set it in your .env file")
    sys.exit(1)

print(f"""
============================================================
           Property Voice Agent - Bland AI Setup
============================================================
  Property: {PROPERTY_NAME}
  API URL:  {API_BASE_URL}
============================================================
""")

# Agent configuration
AGENT_CONFIG = {
    "prompt": f"""You are a professional, friendly property management assistant for {PROPERTY_NAME}.

PERSONALITY:
- Warm, friendly, and genuinely helpful
- Professional but conversational - like a helpful concierge
- Patient and understanding, especially for frustrated callers
- Clear communicator who confirms important details
- Empathetic listener who acknowledges concerns

YOUR ROLE:
You handle all incoming calls for the property, including:
1. Leasing inquiries from prospective tenants
2. Maintenance requests from current residents  
3. Payment and billing questions
4. General inquiries about the property

CONVERSATION GUIDELINES:

GREETING:
Start with: "Thank you for calling {PROPERTY_NAME}, this is your virtual assistant. How can I help you today?"

FOR LEASING INQUIRIES:
- Ask about their ideal move-in date
- Ask about the number of bedrooms they need
- Ask about their budget range
- Use the check_unit_availability tool to find matching units
- Offer to schedule a tour using the schedule_tour tool
- Always get their name, phone, and email for follow-up

FOR MAINTENANCE REQUESTS:
- First, determine if it's an emergency (water leak, no heat, gas smell, etc.)
- Get their unit number
- Get a detailed description of the issue
- Use the create_maintenance_ticket tool
- Provide the ticket number and expected response time
- For emergencies: assure them help is being dispatched immediately

FOR PAYMENT QUESTIONS:
- Use the get_payment_info tool for general information
- For specific account questions, offer to transfer to accounting
- Never discuss specific account balances (privacy)

IMPORTANT RULES:
1. Always verify the unit number for maintenance requests
2. Collect contact information before ending leasing calls
3. Confirm all details before creating tickets or scheduling tours
4. Be honest if you can't help - offer to transfer or callback
5. Thank every caller for reaching out
6. For complex issues, offer to have a manager call back

EMERGENCY KEYWORDS - ALWAYS TREAT AS URGENT:
- Water leak, flooding, burst pipe
- Gas smell, gas leak
- No heat (in winter), no AC (in summer)
- Fire, smoke
- Electrical issues, sparking
- Lockout, security concern
- Sewage backup

END OF CALL:
Always end with: "Is there anything else I can help you with today?" and then "Thank you for calling {PROPERTY_NAME}. Have a great day!"
""",
    
    "voice": "nat",  # Natural female voice - options: nat, maya, josh, matt
    "model": "base",
    "language": "en",
    "max_duration": 600,  # 10 minutes max
    "temperature": 0.7,
    "interruption_threshold": 100,  # Balanced responsiveness
    
    "first_sentence": f"Thank you for calling {PROPERTY_NAME}, this is your virtual assistant. How can I help you today?",
    
    "tools": [
        {
            "name": "check_unit_availability",
            "description": "Check available rental units based on caller's criteria. Use when caller asks about available apartments, units, or rentals.",
            "url": f"{API_BASE_URL}/tools/check-availability",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": {
                "bedrooms": {
                    "type": "number",
                    "description": "Number of bedrooms the caller wants (1, 2, 3, etc.)",
                    "required": False
                },
                "max_rent": {
                    "type": "number", 
                    "description": "Maximum monthly rent budget in dollars",
                    "required": False
                },
                "move_in_date": {
                    "type": "string",
                    "description": "Desired move-in date",
                    "required": False
                }
            }
        },
        {
            "name": "create_maintenance_ticket",
            "description": "Create a maintenance work order ticket. Use when a resident reports an issue that needs repair.",
            "url": f"{API_BASE_URL}/tools/create-ticket",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": {
                "unit_number": {
                    "type": "string",
                    "description": "The resident's unit number (e.g., '101', '2B')",
                    "required": True
                },
                "issue_type": {
                    "type": "string",
                    "description": "Category of the issue (Plumbing, Electrical, HVAC, Appliance, General)",
                    "required": True
                },
                "description": {
                    "type": "string",
                    "description": "Detailed description of the maintenance issue",
                    "required": True
                },
                "urgency": {
                    "type": "string",
                    "description": "Urgency level: 'emergency' for immediate safety issues, 'urgent' for issues affecting livability, 'routine' for everything else",
                    "required": False,
                    "enum": ["emergency", "urgent", "routine"]
                },
                "caller_name": {
                    "type": "string",
                    "description": "Name of the person reporting the issue",
                    "required": False
                }
            }
        },
        {
            "name": "schedule_tour",
            "description": "Schedule a property tour for a prospective tenant. Use when caller wants to visit and see units.",
            "url": f"{API_BASE_URL}/tools/schedule-tour",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": {
                "name": {
                    "type": "string",
                    "description": "Visitor's full name",
                    "required": True
                },
                "phone": {
                    "type": "string",
                    "description": "Visitor's phone number",
                    "required": True
                },
                "email": {
                    "type": "string",
                    "description": "Visitor's email address",
                    "required": False
                },
                "preferred_date": {
                    "type": "string",
                    "description": "Preferred date for the tour (e.g., 'Monday', 'tomorrow', 'February 5th')",
                    "required": False
                },
                "preferred_time": {
                    "type": "string",
                    "description": "Preferred time for the tour (e.g., '2pm', 'morning', 'after 3')",
                    "required": False
                },
                "bedrooms": {
                    "type": "number",
                    "description": "Number of bedrooms interested in",
                    "required": False
                },
                "budget": {
                    "type": "number",
                    "description": "Monthly rent budget",
                    "required": False
                }
            }
        },
        {
            "name": "get_payment_info",
            "description": "Get payment and billing information. Use when caller has questions about rent payments, methods, or policies.",
            "url": f"{API_BASE_URL}/tools/get-payment-info",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": {
                "unit_number": {
                    "type": "string",
                    "description": "Resident's unit number",
                    "required": False
                },
                "inquiry_type": {
                    "type": "string",
                    "description": "Type of payment question (late fees, payment methods, balance, general)",
                    "required": False
                }
            }
        }
    ],
    
    "webhook": f"{API_BASE_URL}/webhooks/bland/call-ended",
    
    "analysis_schema": {
        "call_type": "string - one of: leasing, maintenance, payment, general",
        "caller_name": "string - name of the caller if provided",
        "caller_email": "string - email if provided",
        "unit_number": "string - unit number if mentioned",
        "issue_description": "string - summary of issue or inquiry",
        "action_taken": "string - what action was taken during the call",
        "follow_up_needed": "boolean - whether follow-up is required"
    }
}


def create_agent():
    """Create the Bland AI agent"""
    print("Creating Bland AI agent...")
    
    response = requests.post(
        "https://api.bland.ai/v1/agents",
        headers={
            "Authorization": f"Bearer {BLAND_API_KEY}",
            "Content-Type": "application/json"
        },
        json=AGENT_CONFIG
    )
    
    if response.status_code == 200:
        agent_data = response.json()
        agent = agent_data.get("agent", agent_data)
        
        print(f"""
============================================================
                  Agent Created Successfully!
============================================================

  Agent ID: {agent.get('agent_id', 'N/A')}

------------------------------------------------------------
                        NEXT STEPS:
------------------------------------------------------------

  1. Go to https://app.bland.ai

  2. Purchase a phone number for your agent
     (Settings > Phone Numbers > Purchase)

  3. Assign the phone number to this agent
     (Agents > Select Agent > Settings > Phone Number)

  4. Test by calling your new number!

============================================================
""")
        return agent
    else:
        print(f"[ERROR] Error creating agent: {response.status_code}")
        print(f"   Response: {response.text}")
        return None


def list_agents():
    """List existing Bland AI agents"""
    print("\nFetching existing agents...")
    
    response = requests.get(
        "https://api.bland.ai/v1/agents",
        headers={
            "Authorization": f"Bearer {BLAND_API_KEY}"
        }
    )
    
    if response.status_code == 200:
        agents = response.json().get("agents", [])
        if agents:
            print(f"\nFound {len(agents)} existing agent(s):")
            for agent in agents:
                print(f"  - ID: {agent.get('agent_id')} | Voice: {agent.get('voice', 'N/A')}")
        else:
            print("  No agents found")
        return agents
    else:
        print(f"[ERROR] Error listing agents: {response.text}")
        return []


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Bland AI Agent Setup")
    parser.add_argument("--list", action="store_true", help="List existing agents")
    parser.add_argument("--create", action="store_true", help="Create a new agent")
    args = parser.parse_args()
    
    if args.list:
        list_agents()
    elif args.create:
        create_agent()
    else:
        # Default: show existing agents and prompt to create
        agents = list_agents()
        
        if not agents:
            print("\nNo agents found. Creating a new one...")
            create_agent()
        else:
            response = input("\nWould you like to create a new agent? (y/n): ")
            if response.lower() == 'y':
                create_agent()
            else:
                print("\nTo update an existing agent, use the Bland AI dashboard at https://app.bland.ai")
