# 🚀 Enhanced Features - Contact Recognition, Memory & Troubleshooting

## Overview

The Property Voice Agent now includes advanced features for tenant recognition, conversation memory, and automated troubleshooting assistance.

## New Features

### 1. 📞 Contact Recognition & Validation

**What it does:**
- Automatically identifies callers by phone number
- Retrieves tenant information from database
- Tracks call history
- Personalizes greetings for returning callers

**How it works:**
- Uses Bland AI's **Dynamic Data** feature
- Makes API call to `/tools/validate-contact` at call start
- Populates variables: `{{contact_name}}`, `{{is_tenant}}`, `{{previous_calls}}`
- Agent uses this info for personalized responses

**Example:**
```
Agent: "Hi Sarah, thanks for calling back! I see you called about your Unit 5 toilet issue earlier. 
How can I help you today?"
```

**Technical Implementation:**
- Endpoint: `POST /tools/validate-contact`
- Called via Dynamic Data before call starts
- Returns: contact info, tenant status, call history
- Cached for call duration

### 2. 🧠 Memory & Context Awareness

**What it does:**
- Remembers past conversations automatically
- Links calls by phone number
- Maintains context across multiple calls
- Stores call summaries for future reference

**How to set up:**

1. **Create Memory Store in Bland Dashboard:**
   ```
   https://app.bland.ai/dashboard/memory
   → Create New Memory → "Property Management"
   ```

2. **Attach to Inbound Number:**
   - Edit inbound number settings
   - Under "Knowledge", select your memory store
   - Save changes

3. **Auto-population:**
   - Bland automatically creates user records on first call
   - Stores call summaries after each conversation
   - Recalls information on future calls

**How it works:**
- Bland AI's Memory feature links users by phone number
- After each call, webhook saves call record to Supabase
- Bland stores summary in memory store
- Next call retrieves: previous conversations, metadata, context

**Example conversation:**
```
Call 1: Tenant reports toilet issue in Unit 5
Call 2 (3 days later):
Agent: "Hi again! I have your previous conversation about the toilet in Unit 5. 
I see our maintenance team visited 2 days ago. How did that go? Is everything working now?"
```

### 3. 🔧 Automated Troubleshooting Tips

**What it does:**
- Provides instant troubleshooting steps during maintenance calls
- Categorized by issue type (plumbing, electrical, HVAC, appliances)
- Safety-aware (no DIY tips for emergencies)
- Reduces maintenance calls for self-resolvable issues

**Troubleshooting Database Categories:**
- **Plumbing:** Toilets, sinks, showers, leaks
- **Electrical:** Outlets, lights, circuit breakers
- **HVAC:** Heating, cooling, thermostats, filters
- **Appliances:** Refrigerator, dishwasher, washer/dryer
- **Other:** Door locks, windows, general maintenance

**How it works:**

1. **During Maintenance Call:**
   - Tenant reports issue → Agent creates ticket
   - System automatically generates relevant troubleshooting tips
   - Agent speaks 2-3 key tips to tenant
   - Full tips included in email summary

2. **Urgency-Based Logic:**
   - **Emergency:** No DIY tips - immediate dispatch
   - **Urgent/Routine:** Provides 3-5 actionable steps
   - **Safety warnings** for electrical/gas issues

**Example Tips for "Toilet Won't Flush":**
```
1. Check if the water supply valve behind the toilet is fully open
2. Try flushing - if no water flows, ensure the valve is open
3. Check if the flapper inside the tank is properly sealing
4. For clogs, try using a plunger with firm, steady pressure

Estimated Resolution: Professional maintenance within 1-3 business days
```

**API Endpoints:**
- `POST /tools/get-troubleshooting-tips` - Get tips for specific issue
- Automatically called by `create-ticket` endpoint

### 4. 📧 Enhanced Email Summaries

**What's included:**
- Call transcript
- AI-generated summary
- **Troubleshooting steps provided** (NEW)
- Ticket details with urgency
- Estimated resolution time
- Tenant contact information

**Example Email:**

```html
Subject: Maintenance Call Summary - Unit 5 - Emergency

Call Summary:
Tenant Sarah Johnson (Unit 5) reported toilet flooding - Emergency

Troubleshooting Steps Provided:
1. Turn off water supply valve behind toilet immediately
2. Do not attempt repairs - safety hazard
3. Clear area around toilet
4. Emergency team dispatched

Action Taken:
✓ Emergency ticket created (#1234)
✓ Maintenance team notified
✓ ETA: 0-2 hours

Contact: Sarah Johnson | (630) 943-8357 | sarah@email.com
```

## API Endpoints Reference

### New Endpoints

#### 1. Validate Contact
```http
POST /tools/validate-contact
Content-Type: application/json

{
  "phone_number": "+16309438357"
}

Response:
{
  "contact_found": true,
  "contact_id": "uuid",
  "name": "Sarah Johnson",
  "email": "sarah@email.com",
  "contact_type": "tenant",
  "is_tenant": true,
  "previous_calls": 3,
  "context": "Verified tenant: Sarah Johnson. Previous calls: 3."
}
```

#### 2. Get Troubleshooting Tips
```http
POST /tools/get-troubleshooting-tips
Content-Type: application/json

{
  "issue_type": "plumbing",
  "description": "toilet won't flush",
  "urgency": "routine"
}

Response:
{
  "response": "While waiting for our maintenance team, here are some troubleshooting steps you can try: 1. Check if the water supply valve behind the toilet is fully open. 2. Try flushing - if no water flows, ensure the valve is open...",
  "tips": [
    "Check if the water supply valve behind the toilet is fully open",
    "Try flushing - if no water flows, ensure the valve is open",
    "Check if the flapper inside the tank is properly sealing"
  ],
  "estimated_resolution": "Professional maintenance: 1-3 business days",
  "can_self_resolve": true
}
```

## Configuration Files

### Bland AI Configuration

The enhanced configuration includes:

```python
{
  "dynamic_data": [
    {
      "url": "{API_BASE_URL}/tools/validate-contact",
      "method": "POST",
      "body": {"phone_number": "{{phone_number}}"},
      "response_data": [
        {"name": "contact_name", "data": "$.name"},
        {"name": "is_tenant", "data": "$.is_tenant"},
        {"name": "previous_calls", "data": "$.previous_calls"}
      ]
    }
  ],
  "tools": [
    // ... existing tools ...
    {
      "name": "get_troubleshooting_tips",
      "url": "{API_BASE_URL}/tools/get-troubleshooting-tips",
      "method": "POST"
    }
  ]
}
```

## Setup Instructions

### 1. Update Bland AI Configuration

```bash
# Run the enhanced configuration script
cd c:\Users\avide\Desktop\propvoice_mvp
py scripts/configure_bland_enhanced.py
```

### 2. Set Up Memory Store (Optional but Recommended)

1. Go to [Bland AI Dashboard → Memory](https://app.bland.ai/dashboard/memory)
2. Click "Create New Memory"
3. Name it: "Property Management"
4. Go to your inbound number settings
5. Under "Knowledge", select "Property Management" memory store
6. Save

### 3. Test the Features

**Call your number:** +16307963284

**Test scenarios:**

1. **New Caller Test:**
   - Call and report a maintenance issue
   - Should receive generic greeting
   - Get troubleshooting tips

2. **Returning Caller Test:**
   - Call again from same number
   - Should be greeted by name
   - Reference to previous call

3. **Emergency Test:**
   - Report flooding or gas leak
   - Should NOT get DIY tips
   - Immediate dispatch confirmation

4. **Routine Maintenance Test:**
   - Report minor issue (slow drain)
   - Should receive 2-3 troubleshooting tips
   - Ticket created with tips in notes

### 4. Verify in Supabase

Check these tables:
- `contacts` - New contact records created
- `calls` - Call records with contact_id linked
- `maintenance_tickets` - Tickets with troubleshooting tips in notes

### 5. Check Email

You should receive email with:
- Call summary
- Troubleshooting steps provided to tenant
- Ticket details

## Troubleshooting

### Contact Recognition Not Working

**Check:**
1. Server is running on port 8000
2. LocalTunnel is forwarding correctly
3. Dynamic Data is configured in Bland
4. Check server logs for `/tools/validate-contact` calls

**Debug:**
```bash
# Test endpoint directly
Invoke-RestMethod -Uri "http://localhost:8000/tools/validate-contact" `
  -Method POST `
  -Body '{"phone_number":"+16309438357"}' `
  -ContentType "application/json"
```

### Memory Not Working

**Check:**
1. Memory store exists in Bland dashboard
2. Memory store is attached to inbound number
3. Calls are completing successfully
4. Webhook is saving call records to Supabase

### Troubleshooting Tips Not Appearing

**Check:**
1. `app/services/troubleshooting.py` exists
2. Server restarted after code changes
3. Check server logs for errors in `get_troubleshooting_tips`

**Debug:**
```bash
# Test troubleshooting endpoint
Invoke-RestMethod -Uri "http://localhost:8000/tools/get-troubleshooting-tips" `
  -Method POST `
  -Body '{"issue_type":"plumbing","description":"toilet clogged","urgency":"routine"}' `
  -ContentType "application/json"
```

## Benefits

### For Property Managers:
- ✅ Reduced repeat calls (tenants try troubleshooting first)
- ✅ Better call context and history
- ✅ Personalized tenant interactions
- ✅ Comprehensive email summaries
- ✅ Self-service resolution for minor issues

### For Tenants:
- ✅ Recognized and greeted by name
- ✅ Faster resolution with DIY tips
- ✅ No need to repeat information
- ✅ Consistent experience across calls
- ✅ Clear expectations on resolution time

## Future Enhancements

Potential additions:
- SMS delivery of troubleshooting tips
- Photo/video upload for maintenance issues
- Automated follow-up calls
- Predictive maintenance alerts
- Integration with PMS (Yardi, AppFolio, etc.)
- Automated scheduling with calendar integration

## Cost Impact

**Dynamic Data calls:** Minimal (1-2 API calls per inbound call)
**Memory storage:** Free tier sufficient for most properties
**Troubleshooting:** No additional cost (internal logic)

**Expected reduction in maintenance calls:** 15-25% through self-service resolution

---

**Setup Complete?** Test by calling +16307963284 and report a maintenance issue!
