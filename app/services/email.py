"""
Email Service using Resend
Sends formatted call summary emails to property managers
"""
import resend
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Resend
resend.api_key = settings.RESEND_API_KEY


def generate_email_html(call_data: Dict[str, Any], summary: Dict[str, Any]) -> str:
    """
    Generate HTML email content from call data and summary
    """
    # Format action items
    action_items_html = ""
    for item in summary.get("action_items", []):
        action_items_html += f'<li style="padding: 8px 0; border-bottom: 1px solid #eee;">☐ {item}</li>'
    
    if not action_items_html:
        action_items_html = '<li style="padding: 8px 0; color: #888;">No action items</li>'
    
    # Format next steps
    next_steps_html = ""
    for step in summary.get("next_steps", []):
        next_steps_html += f'<li style="padding: 5px 0;">{step}</li>'
    
    if not next_steps_html:
        next_steps_html = '<li style="color: #888;">No follow-up required</li>'
    
    # Format key details based on call type
    key_details_html = ""
    key_details = summary.get("key_details", {})
    
    if key_details:
        for key, value in key_details.items():
            if value:
                formatted_key = key.replace("_", " ").title()
                key_details_html += f'''
                <tr>
                    <td style="padding: 8px 12px; font-weight: bold; color: #4a5568; width: 40%;">{formatted_key}</td>
                    <td style="padding: 8px 12px;">{value}</td>
                </tr>'''
    
    # Format caller info
    caller_info = summary.get("caller_info", {})
    caller_html = ""
    if caller_info.get("name"):
        caller_html += f'<strong>{caller_info["name"]}</strong><br>'
    if caller_info.get("phone"):
        caller_html += f'📱 {caller_info["phone"]}<br>'
    if caller_info.get("email"):
        caller_html += f'📧 {caller_info["email"]}<br>'
    if caller_info.get("unit_number"):
        caller_html += f'🏠 Unit {caller_info["unit_number"]}'
    
    if not caller_html:
        caller_html = f'📱 {call_data.get("from_number", "Unknown")}'
    
    # Format conversation highlights
    highlights_html = ""
    for highlight in summary.get("conversation_highlights", []):
        highlights_html += f'<div style="padding: 10px; margin: 8px 0; background: #f8f9fa; border-left: 3px solid #667eea; font-style: italic;">"{highlight}"</div>'
    
    # Sentiment badge color
    sentiment = summary.get("sentiment", "neutral")
    sentiment_colors = {
        "positive": "#48bb78",
        "neutral": "#a0aec0",
        "negative": "#f56565"
    }
    sentiment_color = sentiment_colors.get(sentiment, "#a0aec0")
    
    # Call type badge color
    call_type = summary.get("call_type", "general")
    type_colors = {
        "leasing": "#667eea",
        "maintenance": "#ed8936",
        "payment": "#48bb78",
        "general": "#a0aec0"
    }
    type_color = type_colors.get(call_type, "#a0aec0")
    
    # Format duration
    duration_seconds = call_data.get("duration", 0)
    duration_minutes = duration_seconds // 60
    duration_remaining_seconds = duration_seconds % 60
    duration_str = f"{duration_minutes}m {duration_remaining_seconds}s" if duration_minutes > 0 else f"{duration_seconds}s"
    
    # Recording link
    recording_html = ""
    if call_data.get("recording_url"):
        recording_html = f'''
        <div style="padding: 20px; border-top: 1px solid #e2e8f0;">
            <h3 style="margin: 0 0 10px 0; color: #2d3748; font-size: 16px;">🎧 Call Recording</h3>
            <a href="{call_data["recording_url"]}" style="display: inline-block; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 6px;">Listen to Recording →</a>
        </div>'''
    
    # Callback alert
    callback_html = ""
    if summary.get("requires_callback"):
        callback_html = f'''
        <div style="padding: 15px; margin: 15px 0; background: #fff5f5; border: 1px solid #fc8181; border-radius: 8px;">
            <strong style="color: #c53030;">⚠️ Callback Required</strong>
            <p style="margin: 5px 0 0 0; color: #742a2a;">{summary.get("callback_reason", "Follow up with caller")}</p>
        </div>'''
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; background: #f7fafc;">
        <div style="max-width: 600px; margin: 0 auto; background: white;">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 25px;">
                <h1 style="margin: 0 0 5px 0; font-size: 24px; font-weight: 600;">📞 Call Summary</h1>
                <p style="margin: 0; opacity: 0.9; font-size: 14px;">{settings.PROPERTY_NAME}</p>
            </div>
            
            <!-- Badges -->
            <div style="padding: 15px 25px; background: #f7fafc; border-bottom: 1px solid #e2e8f0;">
                <span style="display: inline-block; padding: 4px 12px; background: {type_color}; color: white; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-right: 8px;">{call_type}</span>
                <span style="display: inline-block; padding: 4px 12px; background: {sentiment_color}; color: white; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: uppercase;">{sentiment}</span>
            </div>
            
            <!-- Call Details -->
            <div style="padding: 20px 25px; border-bottom: 1px solid #e2e8f0;">
                <h3 style="margin: 0 0 15px 0; color: #2d3748; font-size: 16px;">📋 Call Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; color: #718096; width: 30%;">From</td>
                        <td style="padding: 8px 0;">{caller_html}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #718096;">Duration</td>
                        <td style="padding: 8px 0;">{duration_str}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #718096;">Time</td>
                        <td style="padding: 8px 0;">{call_data.get("started_at", "Unknown")}</td>
                    </tr>
                </table>
            </div>
            
            {callback_html}
            
            <!-- Overview -->
            <div style="padding: 20px 25px; border-bottom: 1px solid #e2e8f0;">
                <h3 style="margin: 0 0 10px 0; color: #2d3748; font-size: 16px;">📝 Overview</h3>
                <p style="margin: 0; color: #4a5568;">{summary.get("overview", "No summary available")}</p>
            </div>
            
            <!-- Action Items -->
            <div style="padding: 20px 25px; border-bottom: 1px solid #e2e8f0;">
                <h3 style="margin: 0 0 10px 0; color: #2d3748; font-size: 16px;">✅ Action Items</h3>
                <ul style="margin: 0; padding: 0; list-style: none;">
                    {action_items_html}
                </ul>
            </div>
            
            <!-- Key Details -->
            {f'''<div style="padding: 20px 25px; border-bottom: 1px solid #e2e8f0;">
                <h3 style="margin: 0 0 10px 0; color: #2d3748; font-size: 16px;">📊 Key Details</h3>
                <table style="width: 100%; border-collapse: collapse; background: #f7fafc; border-radius: 8px;">
                    {key_details_html}
                </table>
            </div>''' if key_details_html else ''}
            
            <!-- Conversation Highlights -->
            {f'''<div style="padding: 20px 25px; border-bottom: 1px solid #e2e8f0;">
                <h3 style="margin: 0 0 10px 0; color: #2d3748; font-size: 16px;">💬 Conversation Highlights</h3>
                {highlights_html}
            </div>''' if highlights_html else ''}
            
            <!-- Next Steps -->
            <div style="padding: 20px 25px; border-bottom: 1px solid #e2e8f0;">
                <h3 style="margin: 0 0 10px 0; color: #2d3748; font-size: 16px;">➡️ Next Steps</h3>
                <ul style="margin: 0; padding-left: 20px; color: #4a5568;">
                    {next_steps_html}
                </ul>
            </div>
            
            {recording_html}
            
            <!-- Footer -->
            <div style="padding: 20px 25px; background: #f7fafc; text-align: center;">
                <p style="margin: 0; color: #a0aec0; font-size: 12px;">
                    This summary was automatically generated by Property Voice AI<br>
                    Call ID: {call_data.get("bland_call_id", call_data.get("id", "Unknown"))}
                </p>
            </div>
            
        </div>
    </body>
    </html>
    '''
    
    return html


async def send_call_summary_email(
    call_data: Dict[str, Any],
    summary: Dict[str, Any],
    recipient_email: Optional[str] = None
) -> bool:
    """
    Send a call summary email via Resend
    
    Args:
        call_data: The call record data
        summary: The generated summary
        recipient_email: Email to send to (defaults to MANAGER_EMAIL)
        
    Returns:
        True if email sent successfully, False otherwise
    """
    recipient = recipient_email or settings.MANAGER_EMAIL
    
    if not recipient:
        logger.warning("No recipient email configured")
        return False
    
    try:
        # Generate email HTML
        html_content = generate_email_html(call_data, summary)
        
        # Generate subject line
        call_type = summary.get("call_type", "general").title()
        caller_name = summary.get("caller_info", {}).get("name", "")
        from_number = call_data.get("from_number", "Unknown")
        
        if caller_name:
            subject = f"📞 {call_type} Call - {caller_name} - {settings.PROPERTY_NAME}"
        else:
            subject = f"📞 {call_type} Call - {from_number} - {settings.PROPERTY_NAME}"
        
        # Add urgency indicator for emergencies
        if summary.get("key_details", {}).get("urgency") == "emergency":
            subject = f"🚨 URGENT: {subject}"
        
        # Send email via Resend
        email_response = resend.Emails.send({
            "from": f"Property Voice AI <onboarding@resend.dev>",  # Use your verified domain
            "to": [recipient],
            "subject": subject,
            "html": html_content
        })
        
        logger.info(f"Email sent successfully to {recipient}, ID: {email_response.get('id')}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False
