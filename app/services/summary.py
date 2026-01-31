"""
AI Summary Generation Service
Uses OpenAI GPT-4 to generate structured summaries from call transcripts
"""
from openai import OpenAI
from typing import Dict, Any, Optional
import json
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI client
_openai_client: Optional[OpenAI] = None


def get_openai_client() -> OpenAI:
    """Get or create OpenAI client instance"""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


SUMMARY_SYSTEM_PROMPT = """You are a property management assistant that analyzes call transcripts and extracts structured information.

Your task is to:
1. Identify the type of call (leasing, maintenance, payment, or general)
2. Extract key information based on the call type
3. List action items that need follow-up
4. Determine the sentiment of the call
5. Summarize the conversation clearly

Be concise but thorough. Focus on actionable information."""


SUMMARY_USER_PROMPT = """Analyze this property management call transcript and return a structured JSON response.

TRANSCRIPT:
{transcript}

Return a JSON object with this exact structure:
{{
    "call_type": "leasing" | "maintenance" | "payment" | "general",
    "overview": "Brief 2-3 sentence summary of the call",
    "sentiment": "positive" | "neutral" | "negative",
    "caller_info": {{
        "name": "Caller's name if mentioned",
        "phone": "Phone number if mentioned",
        "email": "Email if mentioned",
        "unit_number": "Unit number if tenant/resident"
    }},
    "action_items": [
        "List of specific actions that need to be taken"
    ],
    "key_details": {{
        // For leasing calls:
        "move_in_date": "Desired move-in date",
        "bedrooms_requested": "Number of bedrooms",
        "budget": "Maximum rent budget",
        "tour_scheduled": "Tour date/time if scheduled",
        
        // For maintenance calls:
        "issue_type": "Type of maintenance issue",
        "urgency": "emergency | urgent | routine",
        "issue_description": "Detailed description",
        "location_in_unit": "Where in the unit",
        "ticket_created": "Ticket number if created",
        
        // For payment calls:
        "inquiry_type": "Type of payment inquiry",
        "amount_discussed": "Any amounts mentioned",
        "payment_arrangement": "Any arrangements made"
    }},
    "conversation_highlights": [
        "Key quotes or important exchanges from the call"
    ],
    "next_steps": [
        "List of next steps for follow-up"
    ],
    "requires_callback": true | false,
    "callback_reason": "Reason for callback if required"
}}

Only include fields that are relevant to the call type. Use null for missing information."""


async def generate_call_summary(transcript: str) -> Dict[str, Any]:
    """
    Generate a structured summary from a call transcript using GPT-4
    
    Args:
        transcript: The full call transcript text
        
    Returns:
        Dictionary containing the structured summary
    """
    if not transcript or len(transcript.strip()) < 10:
        return {
            "call_type": "general",
            "overview": "Call transcript too short to analyze",
            "sentiment": "neutral",
            "caller_info": {},
            "action_items": [],
            "key_details": {},
            "conversation_highlights": [],
            "next_steps": [],
            "requires_callback": False,
            "callback_reason": None
        }
    
    try:
        client = get_openai_client()
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using gpt-4o-mini for cost efficiency
            messages=[
                {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                {"role": "user", "content": SUMMARY_USER_PROMPT.format(transcript=transcript)}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,  # Lower temperature for more consistent outputs
            max_tokens=1500
        )
        
        summary_text = response.choices[0].message.content
        summary = json.loads(summary_text)
        
        logger.info(f"Generated summary for call type: {summary.get('call_type')}")
        return summary
    
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse summary JSON: {e}")
        return {
            "call_type": "general",
            "overview": "Error parsing call summary",
            "sentiment": "neutral",
            "action_items": ["Review call recording manually"],
            "error": str(e)
        }
    
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return {
            "call_type": "general",
            "overview": f"Error generating summary: {str(e)}",
            "sentiment": "neutral",
            "action_items": ["Review call recording manually"],
            "error": str(e)
        }


async def analyze_urgency(description: str) -> str:
    """
    Analyze a maintenance description to determine urgency level
    
    Returns: 'emergency', 'urgent', or 'routine'
    """
    emergency_keywords = [
        'flood', 'flooding', 'water leak', 'burst pipe', 'gas leak', 'gas smell',
        'no heat', 'no hot water', 'no electricity', 'power out', 'fire',
        'smoke', 'break in', 'broken door', 'broken window', 'locked out',
        'sewage', 'toilet overflow', 'electrical spark', 'sparking'
    ]
    
    urgent_keywords = [
        'no ac', 'no air conditioning', 'refrigerator not working', 'fridge broken',
        'stove not working', 'oven broken', 'dishwasher leak', 'washing machine leak',
        'toilet running', 'sink clogged', 'drain clogged'
    ]
    
    description_lower = description.lower()
    
    for keyword in emergency_keywords:
        if keyword in description_lower:
            return 'emergency'
    
    for keyword in urgent_keywords:
        if keyword in description_lower:
            return 'urgent'
    
    return 'routine'
