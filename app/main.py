"""
Property Voice Agent - Main FastAPI Application
Handles Bland AI tool calls and webhooks for property management voice agent
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional
import logging
import json

from app.config import settings
from app.services import database as db
from app.services.summary import generate_call_summary, analyze_urgency
from app.services.email import send_call_summary_email

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("🚀 Property Voice Agent starting up...")
    logger.info(f"📍 API Base URL: {settings.API_BASE_URL}")
    logger.info(f"🏠 Property: {settings.PROPERTY_NAME}")
    yield
    logger.info("👋 Property Voice Agent shutting down...")


app = FastAPI(
    title="Property Voice Agent API",
    description="AI-powered voice agent for property management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================================
# HEALTH & INFO ROUTES
# ===========================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Property Voice Agent API",
        "version": "1.0.0",
        "property": settings.PROPERTY_NAME,
        "status": "running",
        "endpoints": {
            "tools": [
                "/tools/check-availability",
                "/tools/create-ticket",
                "/tools/schedule-tour",
                "/tools/get-payment-info"
            ],
            "webhooks": [
                "/webhooks/bland/call-ended"
            ],
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "property": settings.PROPERTY_NAME
    }


@app.get("/debug/test-db")
async def debug_test_db():
    """Debug: test Supabase insert (call record)"""
    import requests
    from app.config import settings
    url = f"{(settings.SUPABASE_URL or '').rstrip('/')}/rest/v1/calls"
    if not url or url == "/rest/v1/calls":
        return {"error": "SUPABASE_URL not set", "url": url}
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    data = {"bland_call_id": "debug-test", "from_number": "+1", "duration": 0, "status": "completed"}
    try:
        r = requests.post(url, headers=headers, json=data, timeout=10)
        return {"status": r.status_code, "ok": r.ok, "text": r.text[:300]}
    except Exception as e:
        return {"error": str(e)}


@app.get("/debug/test-email")
async def debug_test_email():
    """Debug: test email summary (OpenAI + Resend)"""
    if not settings.MANAGER_EMAIL:
        return {"error": "MANAGER_EMAIL not set in .env"}
    sample_call = {
        "id": "test-email",
        "bland_call_id": "debug-email-test",
        "from_number": "+16309438357",
        "duration": 90,
        "started_at": datetime.now().isoformat(),
        "recording_url": None,
    }
    sample_transcript = (
        "Agent: Thank you for calling Desai Property. Caller: Hi, I'm looking for a 2 bedroom "
        "under 1800. Agent: I found Unit 201 at 1650 and Unit 203 at 1550. Caller: I'd like to "
        "schedule a tour for Saturday. Agent: I've noted that. Can I get your name and email?"
    )
    try:
        summary = await generate_call_summary(sample_transcript)
        email_sent = await send_call_summary_email(
            call_data=sample_call,
            summary=summary,
            recipient_email=settings.MANAGER_EMAIL,
        )
        return {
            "status": "success" if email_sent else "failed",
            "email_sent": email_sent,
            "recipient": settings.MANAGER_EMAIL,
            "summary_type": summary.get("call_type", "unknown"),
        }
    except Exception as e:
        logger.exception("Email test failed")
        return {"error": str(e), "status": "failed"}


# ===========================================
# TOOL ENDPOINTS (Called by Bland AI during calls)
# ===========================================

@app.post("/tools/check-availability")
async def check_availability(request: Request):
    """
    Check available rental units based on criteria.
    Called by Bland AI when caller asks about available units.
    
    Expected parameters from Bland:
    - bedrooms: Number of bedrooms (optional)
    - max_rent: Maximum monthly rent (optional)
    - move_in_date: Desired move-in date (optional)
    """
    try:
        data = await request.json()
        logger.info(f"📞 Check availability request: {data}")
        
        bedrooms = data.get("bedrooms")
        max_rent = data.get("max_rent")
        
        # Convert bedrooms to int if provided as string
        if bedrooms and isinstance(bedrooms, str):
            try:
                bedrooms = int(bedrooms)
            except ValueError:
                bedrooms = None
        
        # Convert max_rent to float if provided as string
        if max_rent and isinstance(max_rent, str):
            try:
                max_rent = float(max_rent.replace("$", "").replace(",", ""))
            except ValueError:
                max_rent = None
        
        # Query available units
        units = await db.get_available_units(
            bedrooms=bedrooms,
            max_rent=max_rent
        )
        
        if not units:
            # Check if we have ANY available units
            all_units = await db.get_available_units()
            
            if not all_units:
                return {
                    "response": "I apologize, but we don't have any units available at the moment. "
                               "However, I'd be happy to add you to our waitlist so you're the first to know when something opens up. "
                               "Can I get your email address?"
                }
            else:
                return {
                    "response": f"I don't have any units that match those exact criteria, but we do have {len(all_units)} "
                               f"other units available. Would you like me to tell you about those options instead?"
                }
        
        # Format response for the AI to speak
        if len(units) == 1:
            unit = units[0]
            response = (
                f"Great news! I found a {unit['bedrooms']} bedroom, {unit['bathrooms']} bathroom unit available. "
                f"It's unit {unit['unit_number']}, {unit.get('square_feet', 'spacious')} square feet, "
                f"for ${unit['rent']:,.0f} per month. "
            )
            if unit.get('amenities'):
                response += f"It includes {', '.join(unit['amenities'][:3])}. "
            response += "Would you like to schedule a tour to see it?"
        else:
            response = f"I found {len(units)} units that might work for you. Let me tell you about the top options:\n\n"
            
            for i, unit in enumerate(units[:3], 1):
                response += (
                    f"Option {i}: Unit {unit['unit_number']} - "
                    f"{unit['bedrooms']} bedroom, {unit['bathrooms']} bath for ${unit['rent']:,.0f} per month. "
                )
            
            response += "\nWould you like more details on any of these, or would you like to schedule tours?"
        
        return {"response": response}
    
    except Exception as e:
        logger.error(f"Error in check_availability: {e}")
        return {
            "response": "I'm having a bit of trouble accessing our availability system right now. "
                       "Let me connect you with our leasing office directly, or I can take your contact information "
                       "and have someone call you back within the hour."
        }


@app.post("/tools/create-ticket")
async def create_maintenance_ticket(request: Request):
    """
    Create a maintenance ticket/work order.
    Called by Bland AI when caller reports a maintenance issue.
    
    Expected parameters from Bland:
    - unit_number: Unit number (required)
    - issue_type: Type of issue (required)
    - description: Detailed description (required)
    - urgency: emergency/urgent/routine (optional - will auto-detect)
    - caller_name: Name of the caller (optional)
    - caller_phone: Phone number (optional)
    """
    try:
        data = await request.json()
        logger.info(f"🔧 Create ticket request: {data}")
        
        unit_number = data.get("unit_number")
        issue_type = data.get("issue_type", "General Maintenance")
        description = data.get("description", "")
        urgency = data.get("urgency")
        
        # Validate unit number
        if not unit_number:
            return {
                "response": "I need your unit number to create a maintenance ticket. What unit do you live in?"
            }
        
        # Find the unit
        unit = await db.get_unit_by_number(unit_number)
        
        if not unit:
            return {
                "response": f"I couldn't find unit {unit_number} in our system. "
                           f"Could you double-check that unit number for me? "
                           f"It should be something like 101, 2B, or similar."
            }
        
        # Auto-detect urgency if not provided
        if not urgency:
            urgency = await analyze_urgency(description)
        
        # Create the ticket
        ticket_data = {
            "unit_id": unit["id"],
            "property_id": unit.get("property_id"),
            "issue_type": issue_type,
            "urgency": urgency,
            "description": description,
            "status": "open"
        }
        
        ticket = await db.create_maintenance_ticket(ticket_data)
        
        if not ticket:
            return {
                "response": "I apologize, but I'm having trouble creating the ticket right now. "
                           "Let me transfer you to our maintenance team directly."
            }
        
        # Format response based on urgency
        ticket_number = ticket.get("ticket_number", str(ticket["id"])[:8])
        
        urgency_responses = {
            "emergency": (
                f"I've created an emergency work order, ticket number {ticket_number}. "
                f"I'm dispatching our emergency maintenance team right now. "
                f"Someone will be there within 2 hours. Please make sure they can access your unit. "
                f"Is there anything else you need while you wait?"
            ),
            "urgent": (
                f"I've created an urgent maintenance ticket, number {ticket_number}. "
                f"Our team will be out within 24 hours to take care of this. "
                f"We'll call you before arriving. Is there a specific time that works best for you?"
            ),
            "routine": (
                f"I've created maintenance ticket number {ticket_number} for you. "
                f"Our team will schedule this within 3 to 5 business days. "
                f"We'll call you the day before to confirm a time. "
                f"Is there anything else I can help you with today?"
            )
        }
        
        return {"response": urgency_responses.get(urgency, urgency_responses["routine"])}
    
    except Exception as e:
        logger.error(f"Error in create_ticket: {e}")
        return {
            "response": "I apologize, but I'm having technical difficulties creating that ticket. "
                       "Let me transfer you to our maintenance line so you can speak with someone directly."
        }


@app.post("/tools/schedule-tour")
async def schedule_tour(request: Request):
    """
    Schedule a property tour for a prospective tenant.
    Called by Bland AI when caller wants to see a unit.
    
    Expected parameters from Bland:
    - name: Visitor's name (required)
    - phone: Phone number (required)
    - email: Email address (optional)
    - preferred_date: Preferred tour date (optional)
    - preferred_time: Preferred tour time (optional)
    - bedrooms: Number of bedrooms interested in (optional)
    - budget: Monthly budget (optional)
    """
    try:
        data = await request.json()
        logger.info(f"📅 Schedule tour request: {data}")
        
        name = data.get("name")
        phone = data.get("phone")
        email = data.get("email")
        preferred_date = data.get("preferred_date") or data.get("date")
        preferred_time = data.get("preferred_time") or data.get("time")
        
        # Validate required fields
        if not name:
            return {
                "response": "I'd be happy to schedule a tour for you! May I have your name please?"
            }
        
        if not phone and not email:
            return {
                "response": f"Thanks, {name}! What's the best phone number or email to reach you at?"
            }
        
        # Create or find contact
        contact = await db.find_or_create_contact(
            phone=phone or "",
            name=name,
            email=email,
            contact_type="prospect"
        )
        
        # Create tour request
        tour_data = {
            "visitor_name": name,
            "visitor_phone": phone,
            "visitor_email": email,
            "preferred_date": preferred_date,
            "preferred_time": preferred_time,
            "bedrooms_interested": data.get("bedrooms"),
            "max_budget": data.get("budget"),
            "move_in_date": data.get("move_in_date"),
            "status": "pending"
        }
        
        tour = await db.create_tour_request(tour_data)
        
        if tour:
            if preferred_date and preferred_time:
                response = (
                    f"Wonderful, {name}! I've scheduled your tour for {preferred_date} at {preferred_time}. "
                    f"You'll receive a confirmation email shortly with all the details. "
                    f"Our leasing office is located at the main entrance. "
                    f"Is there anything specific you'd like us to prepare for your visit?"
                )
            elif preferred_date:
                response = (
                    f"Great, {name}! I've noted your preference for {preferred_date}. "
                    f"Our leasing team will call you shortly to confirm the exact time. "
                    f"Is morning or afternoon generally better for you?"
                )
            else:
                response = (
                    f"Perfect, {name}! I've added you to our tour schedule. "
                    f"Our leasing team will reach out within the next few hours to find a time that works for you. "
                    f"In the meantime, is there anything specific you'd like to know about the property?"
                )
            
            return {"response": response}
        else:
            return {
                "response": f"I apologize {name}, I'm having trouble with our scheduling system. "
                           f"Let me take your information and have our leasing team call you directly. "
                           f"They'll reach out within the hour. What's the best number to reach you?"
            }
    
    except Exception as e:
        logger.error(f"Error in schedule_tour: {e}")
        return {
            "response": "I apologize, I'm having some technical difficulties. "
                       "Let me transfer you to our leasing office directly."
        }


@app.post("/tools/get-payment-info")
async def get_payment_info(request: Request):
    """
    Provide payment information and portal details.
    Called by Bland AI when caller has payment questions.
    
    Expected parameters from Bland:
    - unit_number: Unit number (optional)
    - inquiry_type: Type of payment inquiry (optional)
    """
    try:
        data = await request.json()
        logger.info(f"💳 Payment info request: {data}")
        
        inquiry_type = data.get("inquiry_type", "general")
        
        # Base payment information
        response = (
            "For rent payments, you have several convenient options. "
            "You can pay online through our resident portal at payments dot sunsetapts dot com, "
            "where you can set up auto-pay or make one-time payments with a credit card or bank transfer. "
            "You can also drop off a check or money order at our leasing office during business hours, "
            "Monday through Friday, 9 AM to 5 PM. "
        )
        
        # Add specific info based on inquiry type
        if "late" in inquiry_type.lower():
            response += (
                "Regarding late fees, rent is due on the 1st of each month, "
                "with a grace period until the 5th. "
                "After the 5th, a late fee of $50 applies. "
                "If you're experiencing financial hardship, I recommend speaking with our manager "
                "about possible payment arrangements."
            )
        elif "balance" in inquiry_type.lower():
            response += (
                "To check your current balance, you can log into the resident portal "
                "or call our office directly and they can look that up for you."
            )
        else:
            response += (
                "Would you like me to connect you with our accounting team for more specific questions, "
                "or is there anything else I can help you with?"
            )
        
        return {"response": response}
    
    except Exception as e:
        logger.error(f"Error in get_payment_info: {e}")
        return {
            "response": "I apologize, let me transfer you to our accounting team for payment questions."
        }


# ===========================================
# WEBHOOK ENDPOINTS (Called by Bland AI after calls)
# ===========================================

@app.post("/webhooks/bland/call-ended")
async def bland_call_ended_webhook(request: Request):
    """
    Webhook called by Bland AI when a call ends.
    Saves call data, generates summary, and sends email.
    """
    try:
        data = await request.json()
        logger.info(f"📞 Call ended webhook received")
        logger.debug(f"Webhook data: {json.dumps(data, indent=2)}")
        
        # Extract call data from Bland webhook
        call_record = {
            "bland_call_id": data.get("call_id"),
            "from_number": data.get("from") or data.get("to_number"),  # Bland uses different field names
            "to_number": data.get("to") or data.get("from_number"),
            "duration": data.get("call_length") or data.get("duration", 0),
            "transcript": data.get("concatenated_transcript") or data.get("transcript", ""),
            "recording_url": data.get("recording_url"),
            "started_at": data.get("created_at") or datetime.now().isoformat(),
            "ended_at": datetime.now().isoformat(),
            "status": "completed",
            "metadata": data.get("variables", {})
        }
        
        # Save call to database
        saved_call = await db.create_call_record(call_record)
        
        if not saved_call:
            logger.error("Failed to save call record", extra={"call_record": call_record})
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "Failed to save call record", "debug": "Check server logs for REST API error"}
            )
        
        call_id = saved_call["id"]
        logger.info(f"✅ Call saved with ID: {call_id}")
        
        # Generate AI summary if we have a transcript
        transcript = call_record.get("transcript", "")
        
        if transcript and len(transcript) > 20:
            logger.info("🤖 Generating AI summary...")
            summary = await generate_call_summary(transcript)
            
            # Update call with summary
            await db.update_call_record(call_id, {
                "summary": summary,
                "call_type": summary.get("call_type", "general"),
                "sentiment": summary.get("sentiment", "neutral")
            })
            
            # Send email summary
            logger.info(f"📧 Sending email to {settings.MANAGER_EMAIL}...")
            email_sent = await send_call_summary_email(
                call_data={**call_record, "id": call_id},
                summary=summary,
                recipient_email=settings.MANAGER_EMAIL
            )
            
            if email_sent:
                await db.update_call_record(call_id, {
                    "email_sent": True,
                    "email_sent_at": datetime.now().isoformat()
                })
                logger.info("✅ Email sent successfully")
            else:
                logger.warning("⚠️ Failed to send email")
        else:
            logger.info("ℹ️ No transcript available, skipping summary generation")
        
        return {
            "status": "success",
            "call_id": str(call_id),
            "message": "Call processed successfully"
        }
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


# ===========================================
# ERROR HANDLERS
# ===========================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


# ===========================================
# RUN APPLICATION
# ===========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
