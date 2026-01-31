/**
 * Bland AI Send Call - Test Script
 * 
 * Run this to send a test call to your phone number.
 * Replace API_KEY with your Bland API key and phone_number with your number.
 * 
 * Requires: npm install axios (or use fetch)
 */

const API_KEY = 'YOUR_BLAND_API_KEY';  // From .env BLAND_API_KEY
const PHONE_NUMBER = '+16309438357';   // Number to call (yours for testing)
const API_BASE_URL = 'https://acerbic-madalynn-nonthoracic.ngrok-free.dev';  // Your ngrok URL

const task = `You are a professional, friendly property management assistant for Desai Property.

PERSONALITY:
- Warm, friendly, and genuinely helpful
- Professional but conversational - like a helpful concierge
- Patient and understanding, especially for frustrated callers

YOUR ROLE:
You handle property management calls: leasing inquiries, maintenance requests, payment questions, and general inquiries.

GREETING:
Start with: "Thank you for calling Desai Property, this is your virtual assistant. How can I help you today?"

FOR LEASING: Ask about move-in date, bedrooms, budget. Use check_unit_availability tool. Offer to schedule tours.
FOR MAINTENANCE: Get unit number and description. Use create_maintenance_ticket tool. Determine urgency (emergency/urgent/routine).
FOR PAYMENT: Use get_payment_info tool. For specific accounts, offer to transfer to accounting.

IMPORTANT: Always verify unit numbers. Collect contact info for leasing calls. Thank callers.
END OF CALL: "Is there anything else I can help you with today?" then "Thank you for calling Desai Property. Have a great day!"`;

const tools = [
  {
    name: "check_unit_availability",
    description: "Check available rental units. Use when caller asks about apartments or availability.",
    url: `${API_BASE_URL}/tools/check-availability`,
    method: "POST",
    parameters: { bedrooms: "number", max_rent: "number" }
  },
  {
    name: "create_maintenance_ticket",
    description: "Create maintenance work order. Use when resident reports an issue.",
    url: `${API_BASE_URL}/tools/create-ticket`,
    method: "POST",
    parameters: { unit_number: "string", issue_type: "string", description: "string", urgency: "string" }
  },
  {
    name: "schedule_tour",
    description: "Schedule property tour for prospective tenant.",
    url: `${API_BASE_URL}/tools/schedule-tour`,
    method: "POST",
    parameters: { name: "string", phone: "string", email: "string", preferred_date: "string", preferred_time: "string" }
  },
  {
    name: "get_payment_info",
    description: "Get payment and billing information.",
    url: `${API_BASE_URL}/tools/get-payment-info`,
    method: "POST",
    parameters: { inquiry_type: "string" }
  }
];

const data = {
  phone_number: PHONE_NUMBER,
  task: task,
  voice: "nat",
  wait_for_greeting: false,
  record: true,
  answered_by_enabled: true,
  noise_cancellation: false,
  interruption_threshold: 100,
  block_interruptions: false,
  max_duration: 10,
  model: "base",
  language: "babel-en",
  background_track: "none",
  endpoint: "https://api.bland.ai",
  voicemail_action: "hangup",
  tools: tools,
  webhook: `${API_BASE_URL}/webhooks/bland/call-ended`,
  first_sentence: "Thank you for calling Desai Property, this is your virtual assistant. How can I help you today?"
};

// Using fetch (no axios needed)
fetch('https://api.bland.ai/v1/calls', {
  method: 'POST',
  headers: {
    'Authorization': API_KEY,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
})
.then(r => r.json())
.then(result => console.log('Call result:', result))
.catch(err => console.error('Error:', err));
