"""
Supabase Database Service
Handles all database operations for the Property Voice Agent
Uses REST API for writes to avoid supabase-py client compatibility issues.
"""
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import requests

from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Supabase client
_supabase_client: Optional[Client] = None


def _get_rest_config():
    """Get REST API config (lazy load for correct env)"""
    url = (settings.SUPABASE_URL or "").rstrip("/")
    if not url:
        return None, None
    return f"{url}/rest/v1", {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def get_supabase() -> Client:
    """Get or create Supabase client instance"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
    return _supabase_client


def _rest_insert(table: str, data: dict) -> Optional[dict]:
    """Insert via Supabase REST API (bypasses client issues)"""
    try:
        rest_url, headers = _get_rest_config()
        if not rest_url:
            logger.error("SUPABASE_URL not configured")
            return None
        r = requests.post(f"{rest_url}/{table}", headers=headers, json=data, timeout=30)
        if not r.ok:
            logger.error(f"REST insert failed ({table}): {r.status_code} - {r.text[:500]}")
            return None
        result = r.json()
        return result[0] if result else None
    except Exception as e:
        logger.error(f"REST insert failed ({table}): {e}")
        return None


def _rest_update(table: str, id_value: str, data: dict) -> Optional[dict]:
    """Update via Supabase REST API"""
    try:
        rest_url, headers = _get_rest_config()
        if not rest_url:
            return None
        r = requests.patch(
            f"{rest_url}/{table}",
            headers=headers,
            json=data,
            params={"id": f"eq.{id_value}"},
            timeout=30
        )
        r.raise_for_status()
        result = r.json()
        return result[0] if result else None
    except Exception as e:
        logger.error(f"REST update failed ({table}): {e}")
        return None


# ===========================================
# UNIT OPERATIONS
# ===========================================

async def get_available_units(
    bedrooms: Optional[int] = None,
    max_rent: Optional[float] = None,
    property_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get available units based on criteria
    """
    try:
        supabase = get_supabase()
        query = supabase.table("units").select("*").eq("status", "available")
        
        if bedrooms is not None:
            query = query.eq("bedrooms", bedrooms)
        
        if max_rent is not None:
            query = query.lte("rent", max_rent)
        
        if property_id:
            query = query.eq("property_id", property_id)
        
        result = query.order("rent").limit(10).execute()
        return result.data if result.data else []
    
    except Exception as e:
        logger.error(f"Error getting available units: {e}")
        return []


async def get_unit_by_number(unit_number: str, property_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get a unit by its unit number
    """
    try:
        supabase = get_supabase()
        query = supabase.table("units").select("*").eq("unit_number", unit_number)
        
        if property_id:
            query = query.eq("property_id", property_id)
        
        result = query.limit(1).execute()
        return result.data[0] if result.data else None
    
    except Exception as e:
        logger.error(f"Error getting unit: {e}")
        return None


# ===========================================
# CALL OPERATIONS
# ===========================================

async def create_call_record(call_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create a new call record (uses REST API for reliability)
    """
    allowed_keys = {
        "bland_call_id", "from_number", "to_number", "call_type", "status",
        "started_at", "ended_at", "duration", "recording_url", "transcript",
        "summary", "property_id", "unit_id", "contact_id", "sentiment",
        "resolved", "email_sent", "email_sent_at", "metadata"
    }
    clean_data = {k: v for k, v in call_data.items() if k in allowed_keys}
    clean_data = {k: v for k, v in clean_data.items() if v is not None}
    return _rest_insert("calls", clean_data)


async def update_call_record(call_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update an existing call record (uses REST API)
    """
    return _rest_update("calls", call_id, updates)


async def get_call_by_id(call_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a call record by ID
    """
    try:
        supabase = get_supabase()
        result = supabase.table("calls").select("*").eq("id", call_id).limit(1).execute()
        return result.data[0] if result.data else None
    
    except Exception as e:
        logger.error(f"Error getting call: {e}")
        return None


async def get_call_by_bland_id(bland_call_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a call record by Bland AI call ID
    """
    try:
        supabase = get_supabase()
        result = supabase.table("calls").select("*").eq("bland_call_id", bland_call_id).limit(1).execute()
        return result.data[0] if result.data else None
    
    except Exception as e:
        logger.error(f"Error getting call by Bland ID: {e}")
        return None


# ===========================================
# MAINTENANCE TICKET OPERATIONS
# ===========================================

async def create_maintenance_ticket(ticket_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create a new maintenance ticket
    """
    try:
        supabase = get_supabase()
        result = supabase.table("maintenance_tickets").insert(ticket_data).execute()
        return result.data[0] if result.data else None
    
    except Exception as e:
        logger.error(f"Error creating maintenance ticket: {e}")
        return None


async def get_maintenance_ticket(ticket_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a maintenance ticket by ID
    """
    try:
        supabase = get_supabase()
        result = supabase.table("maintenance_tickets").select("*").eq("id", ticket_id).limit(1).execute()
        return result.data[0] if result.data else None
    
    except Exception as e:
        logger.error(f"Error getting maintenance ticket: {e}")
        return None


# ===========================================
# TOUR REQUEST OPERATIONS
# ===========================================

async def create_tour_request(tour_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create a new tour request
    """
    try:
        supabase = get_supabase()
        result = supabase.table("tour_requests").insert(tour_data).execute()
        return result.data[0] if result.data else None
    
    except Exception as e:
        logger.error(f"Error creating tour request: {e}")
        return None


# ===========================================
# CONTACT OPERATIONS
# ===========================================

async def find_or_create_contact(
    phone: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    contact_type: str = "prospect"
) -> Optional[Dict[str, Any]]:
    """
    Find an existing contact by phone or create a new one
    """
    try:
        supabase = get_supabase()
        
        # Try to find existing contact
        result = supabase.table("contacts").select("*").eq("phone", phone).limit(1).execute()
        
        if result.data:
            # Update existing contact if new info provided
            contact = result.data[0]
            updates = {}
            if name and not contact.get("name"):
                updates["name"] = name
            if email and not contact.get("email"):
                updates["email"] = email
            
            if updates:
                supabase.table("contacts").update(updates).eq("id", contact["id"]).execute()
            
            return contact
        
        # Create new contact
        new_contact = {
            "phone": phone,
            "name": name,
            "email": email,
            "type": contact_type
        }
        result = supabase.table("contacts").insert(new_contact).execute()
        return result.data[0] if result.data else None
    
    except Exception as e:
        logger.error(f"Error finding/creating contact: {e}")
        return None


# ===========================================
# PROPERTY OPERATIONS
# ===========================================

async def get_default_property() -> Optional[Dict[str, Any]]:
    """
    Get the default/first property (for MVP with single property)
    """
    try:
        supabase = get_supabase()
        result = supabase.table("properties").select("*").limit(1).execute()
        return result.data[0] if result.data else None
    
    except Exception as e:
        logger.error(f"Error getting default property: {e}")
        return None
