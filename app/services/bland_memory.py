"""
Bland AI Memory Service
Automatically updates Bland AI's memory store after each call
"""
import requests
import logging
from typing import Optional, Dict
from app.config import settings

logger = logging.getLogger(__name__)

BLAND_API_BASE = "https://api.bland.ai/v1"
MEMORY_STORE_NAME = "Property Management"


def get_or_create_memory_store() -> Optional[str]:
    """
    Get existing memory store ID or create a new one
    Returns memory_id if successful
    """
    try:
        headers = {
            "Authorization": settings.BLAND_API_KEY,
            "Content-Type": "application/json"
        }
        
        # List all memories to find ours
        response = requests.get(
            f"{BLAND_API_BASE}/memory",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            memories = data.get("data", {}).get("memories", [])
            
            # Find existing memory store
            for memory in memories:
                if memory.get("name") == MEMORY_STORE_NAME:
                    memory_id = memory.get("id")
                    logger.info(f"Found existing memory store: {memory_id}")
                    return memory_id
            
            # Create new memory store if not found
            logger.info(f"Creating new memory store: {MEMORY_STORE_NAME}")
            create_response = requests.post(
                f"{BLAND_API_BASE}/memory/create",
                headers=headers,
                json={"name": MEMORY_STORE_NAME},
                timeout=10
            )
            
            if create_response.status_code == 200:
                memory_id = create_response.json().get("data", {}).get("id")
                logger.info(f"Created memory store: {memory_id}")
                return memory_id
            else:
                logger.error(f"Failed to create memory store: {create_response.text}")
                return None
        else:
            logger.error(f"Failed to list memories: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error managing memory store: {e}")
        return None


def update_user_memory(
    phone_number: str,
    call_summary: Dict,
    caller_name: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> bool:
    """
    Update user memory in Bland AI after a call
    Non-blocking with extended timeout to handle Bland AI's API response time
    
    Args:
        phone_number: Caller's phone number
        call_summary: AI-generated call summary
        caller_name: Caller's name (optional)
        metadata: Additional metadata to store (optional)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get memory store ID (with caching)
        memory_id = _get_cached_memory_id()
        if not memory_id:
            logger.info("No memory store available - skipping memory update")
            return False
        
        # Build summary text
        summary_text = _format_summary_for_memory(call_summary, caller_name)
        
        # Build metadata string
        metadata_text = _format_metadata(metadata, caller_name)
        
        # Update user memory via Bland AI API
        headers = {
            "Authorization": settings.BLAND_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "phone_number": phone_number,
            "summary": summary_text,
            "metadata": metadata_text
        }
        
        # Increased timeout and better error handling
        response = requests.post(
            f"{BLAND_API_BASE}/memory/{memory_id}/user/update",
            headers=headers,
            json=payload,
            timeout=30  # Increased from 15 to 30 seconds
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Updated memory for {phone_number}")
            return True
        elif response.status_code == 404:
            logger.warning(f"Memory store not found - may need to recreate")
            return False
        else:
            logger.warning(f"Memory update failed: {response.status_code} - {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        logger.warning(f"Memory update timed out for {phone_number} (Bland API slow - this is normal)")
        return False
    except requests.exceptions.RequestException as e:
        logger.warning(f"Memory update network error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error updating user memory: {e}")
        return False


# Cache for memory store ID
_memory_id_cache = None
_cache_timestamp = None

def _get_cached_memory_id() -> Optional[str]:
    """Get memory ID from cache or fetch it"""
    global _memory_id_cache, _cache_timestamp
    import time
    
    # Cache for 1 hour
    if _memory_id_cache and _cache_timestamp and (time.time() - _cache_timestamp < 3600):
        return _memory_id_cache
    
    # Fetch and cache
    memory_id = get_or_create_memory_store()
    if memory_id:
        _memory_id_cache = memory_id
        _cache_timestamp = time.time()
    
    return memory_id


def _format_summary_for_memory(call_summary: Dict, caller_name: Optional[str] = None) -> str:
    """Format call summary for Bland AI memory storage"""
    summary_parts = []
    
    # Add caller name if available
    if caller_name:
        summary_parts.append(f"Caller: {caller_name}")
    
    # Add call type
    call_type = call_summary.get("call_type", "general")
    summary_parts.append(f"Type: {call_type.title()}")
    
    # Add main summary
    main_summary = call_summary.get("summary", "")
    if main_summary:
        summary_parts.append(main_summary)
    
    # Add key information based on call type
    if call_type == "maintenance":
        if call_summary.get("issue_type"):
            summary_parts.append(f"Issue: {call_summary['issue_type']}")
        if call_summary.get("urgency"):
            summary_parts.append(f"Urgency: {call_summary['urgency']}")
    
    elif call_type == "leasing":
        if call_summary.get("unit_preferences"):
            summary_parts.append(f"Looking for: {call_summary['unit_preferences']}")
        if call_summary.get("move_in_date"):
            summary_parts.append(f"Move-in: {call_summary['move_in_date']}")
    
    # Add action items
    action_items = call_summary.get("action_items", [])
    if action_items:
        summary_parts.append(f"Actions: {', '.join(action_items[:3])}")
    
    return " | ".join(summary_parts)


def _format_metadata(metadata: Optional[Dict], caller_name: Optional[str] = None) -> str:
    """Format metadata for Bland AI memory storage with NAME= format"""
    meta_parts = []
    
    # CRITICAL: Use NAME= format that the agent looks for
    if caller_name:
        meta_parts.append(f"NAME={caller_name}")
    
    if metadata:
        # Add tenant status
        if metadata.get("is_tenant"):
            meta_parts.append("TYPE=Tenant")
        else:
            meta_parts.append("TYPE=Prospect")
        
        # Add unit info
        if metadata.get("unit_number"):
            meta_parts.append(f"UNIT={metadata['unit_number']}")
        
        # Add email
        email = metadata.get("contact_email") or metadata.get("email")
        if email:
            meta_parts.append(f"EMAIL={email}")
    
    return " | ".join(meta_parts) if meta_parts else "Property caller"


def enable_memory_for_inbound(phone_number: str) -> bool:
    """
    Enable memory for an inbound phone number
    This links the memory store to your inbound number
    
    Args:
        phone_number: Inbound phone number (e.g. +16307963284)
    
    Returns:
        True if successful
    """
    try:
        memory_id = get_or_create_memory_store()
        if not memory_id:
            return False
        
        headers = {
            "Authorization": settings.BLAND_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "phone_number": phone_number,
            "memory_id": memory_id
        }
        
        response = requests.post(
            f"{BLAND_API_BASE}/memory/inbound/enable",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Enabled memory for inbound number: {phone_number}")
            return True
        else:
            logger.warning(f"Failed to enable memory for inbound: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error enabling memory for inbound: {e}")
        return False
