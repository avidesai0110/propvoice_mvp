"""
Troubleshooting Tips Service
Provides generic troubleshooting steps for common maintenance issues
"""
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

# Generic troubleshooting tips database
TROUBLESHOOTING_TIPS = {
    "plumbing": {
        "general": [
            "Check if the water supply valve is fully open",
            "Look for any visible leaks under sinks or behind toilets",
            "Try turning the water off and on again at the main valve"
        ],
        "toilet": [
            "Check if the water supply valve behind the toilet is fully open",
            "Try flushing - if no water flows, ensure the valve is open",
            "If overflowing, turn off the water supply valve immediately",
            "Check if the flapper inside the tank is properly sealing",
            "For clogs, try using a plunger with firm, steady pressure"
        ],
        "sink": [
            "Check if the faucet aerator is clogged (unscrew and clean)",
            "For slow drains, try hot water and dish soap first",
            "Check under the sink for visible leaks or loose connections",
            "Ensure the P-trap isn't clogged (place bucket underneath before removing)"
        ],
        "shower": [
            "Check if the showerhead is clogged (soak in vinegar for 30 minutes)",
            "Ensure the water supply valves are fully open",
            "For low pressure, clean the showerhead filter",
            "Check if other fixtures have water to isolate the issue"
        ]
    },
    "electrical": {
        "general": [
            "Check if the circuit breaker has tripped and reset if needed",
            "Try plugging a different device into the same outlet to test",
            "Do NOT attempt to repair electrical issues yourself",
            "If you smell burning or see sparks, evacuate and call 911"
        ],
        "outlet": [
            "Check the circuit breaker panel for tripped breakers",
            "Test with a different device to rule out device issues",
            "Look for GFCI outlets nearby and press the RESET button",
            "Do not use the outlet if it feels hot or looks damaged"
        ],
        "lights": [
            "Try replacing the light bulb first",
            "Check if other lights in the room work",
            "Ensure the light switch is functioning properly",
            "Check the circuit breaker for that area"
        ]
    },
    "hvac": {
        "general": [
            "Check if the thermostat is set to the correct mode (heat/cool)",
            "Ensure the thermostat batteries are working",
            "Check if the air filter needs replacing (do monthly)",
            "Make sure all vents are open and unobstructed"
        ],
        "heating": [
            "Set thermostat to heat mode and 5°F above current temperature",
            "Check if the pilot light is on (if gas furnace)",
            "Ensure vents and radiators aren't blocked by furniture",
            "Replace air filter if it's dirty or clogged"
        ],
        "cooling": [
            "Set thermostat to cool mode and 5°F below current temperature",
            "Check if the outdoor unit is running",
            "Clean or replace the air filter",
            "Ensure outdoor unit isn't blocked by debris or vegetation"
        ]
    },
    "appliance": {
        "general": [
            "Check if the appliance is properly plugged in",
            "Ensure the circuit breaker hasn't tripped",
            "Consult the appliance manual for troubleshooting steps",
            "Check if there's a reset button on the appliance"
        ],
        "refrigerator": [
            "Ensure the temperature is set between 37-40°F",
            "Check if the door seals properly and isn't left open",
            "Clean the condenser coils (usually in back or bottom)",
            "Make sure vents inside aren't blocked by food items"
        ],
        "dishwasher": [
            "Check if the door latches properly",
            "Ensure the water supply valve under the sink is open",
            "Clean the filter at the bottom of the dishwasher",
            "Make sure the spray arms can rotate freely"
        ],
        "washer": [
            "Check if the water supply valves are fully open",
            "Ensure the drain hose isn't kinked or clogged",
            "Clean the lint filter if applicable",
            "Make sure the load is balanced"
        ]
    },
    "door_lock": {
        "general": [
            "Try using WD-40 or graphite lubricant on the lock mechanism",
            "Check if the key is worn or damaged",
            "Ensure the door is properly aligned with the frame",
            "Try the spare key if available"
        ]
    },
    "window": {
        "general": [
            "Check if the window lock is fully disengaged",
            "Clean the window tracks and remove debris",
            "Lubricate the window tracks with silicone spray",
            "Check for visible obstructions or damage"
        ]
    }
}


def get_troubleshooting_tips(
    issue_type: str,
    description: Optional[str] = None,
    urgency: str = "routine"
) -> Dict[str, any]:
    """
    Get troubleshooting tips based on issue type and description
    
    Args:
        issue_type: Type of issue (plumbing, electrical, hvac, etc.)
        description: Detailed description of the issue
        urgency: Urgency level (emergency, urgent, routine)
    
    Returns:
        Dictionary with troubleshooting tips and recommendations
    """
    try:
        issue_type = issue_type.lower().replace(" ", "_")
        
        # For emergencies, don't provide DIY tips - just escalate
        if urgency == "emergency":
            return {
                "tips": [
                    "This is an emergency situation - professional help is on the way",
                    "If there's immediate danger, evacuate and call 911",
                    "Do not attempt to fix this yourself",
                    "Our maintenance team has been notified and will respond immediately"
                ],
                "can_self_resolve": False,
                "estimated_resolution": "Emergency response dispatched",
                "safety_warning": "Please stay safe and do not attempt repairs"
            }
        
        # Get relevant tips based on issue type
        tips = []
        category = None
        subcategory = None
        
        # Try to find specific category
        for cat, subcats in TROUBLESHOOTING_TIPS.items():
            if cat in issue_type or issue_type in cat:
                category = cat
                
                # Try to find specific subcategory from description
                if description:
                    desc_lower = description.lower()
                    for subcat in subcats.keys():
                        if subcat != "general" and (subcat in desc_lower or subcat in issue_type):
                            subcategory = subcat
                            tips.extend(subcats[subcat])
                            break
                
                # Add general tips for this category
                if not tips and "general" in subcats:
                    tips.extend(subcats["general"])
                
                break
        
        # Fallback to general tips
        if not tips:
            tips = [
                "Please document the issue with photos if possible",
                "Note when the problem started and if it's getting worse",
                "Check if the issue affects other areas of your unit",
                "Our maintenance team will assess and resolve the issue"
            ]
        
        # Determine if tenant can potentially self-resolve
        can_self_resolve = urgency == "routine" and category in ["plumbing", "hvac", "appliance"]
        
        # Estimate resolution time
        resolution_time = {
            "emergency": "0-2 hours",
            "urgent": "4-24 hours",
            "routine": "1-3 business days"
        }.get(urgency, "1-3 business days")
        
        return {
            "tips": tips[:5],  # Limit to top 5 tips
            "can_self_resolve": can_self_resolve,
            "estimated_resolution": f"Professional maintenance: {resolution_time}",
            "category": category or "general",
            "subcategory": subcategory,
            "follow_up_message": (
                "Try these steps and let us know if the issue persists. "
                "Our maintenance team will follow up within the estimated timeframe."
            )
        }
    
    except Exception as e:
        logger.error(f"Error generating troubleshooting tips: {e}")
        return {
            "tips": ["Our maintenance team will assess and resolve your issue"],
            "can_self_resolve": False,
            "estimated_resolution": "1-3 business days",
            "category": "general"
        }


def format_tips_for_email(tips_data: Dict) -> str:
    """Format troubleshooting tips for email"""
    tips = tips_data.get("tips", [])
    
    html = "<h3>🔧 Troubleshooting Steps</h3>"
    html += "<p>Before our maintenance team arrives, you can try these steps:</p>"
    html += "<ol>"
    
    for tip in tips:
        html += f"<li>{tip}</li>"
    
    html += "</ol>"
    
    if tips_data.get("safety_warning"):
        html += f"<p><strong>⚠️ Safety Notice:</strong> {tips_data['safety_warning']}</p>"
    
    html += f"<p><strong>Estimated Resolution:</strong> {tips_data.get('estimated_resolution', 'Soon')}</p>"
    html += f"<p>{tips_data.get('follow_up_message', '')}</p>"
    
    return html


def format_tips_for_sms(tips_data: Dict) -> str:
    """Format troubleshooting tips for SMS (160 char limit per message)"""
    tips = tips_data.get("tips", [])
    
    if not tips:
        return "Maintenance request received. Our team will contact you soon."
    
    # SMS format - keep it concise
    message = "Troubleshooting tips:\n"
    for i, tip in enumerate(tips[:3], 1):  # Max 3 tips for SMS
        message += f"{i}. {tip}\n"
    
    message += f"\nETA: {tips_data.get('estimated_resolution', 'Soon')}"
    
    return message
