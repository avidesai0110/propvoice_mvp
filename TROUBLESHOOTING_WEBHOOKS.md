# Supabase Webhook Integration - Troubleshooting Guide

## Current Status

✅ **Server is running** on port 8000  
✅ **ngrok is running** at `https://acerbic-madalynn-nonthoracic.ngrok-free.dev`  
✅ **Webhook endpoint works** (tested locally with `test_webhook.py`)  
✅ **Database integration works** (call saved with ID: `3a426926-d7ef-46f1-a26f-26741dbeb151`)  
✅ **Email integration works** (summary email sent successfully)  
✅ **Inbound number configured** (+16307963284) with webhook URL  

❌ **Issue**: Bland AI is NOT sending webhooks after real phone calls

## Root Cause Analysis

The problem is that **Bland AI is not triggering webhooks for inbound calls** despite the webhook URL being configured. This could be due to:

1. **Webhook events not enabled** - The `webhook_events` array is empty in Bland's response
2. **Inbound webhook behavior** - Inbound calls may have different webhook triggers than outbound
3. **Network/ngrok issues** - Bland's servers might not be able to reach your ngrok URL
4. **Call completion status** - Webhooks may only fire for specific call statuses

## What I Fixed

### 1. Enhanced Webhook Handler (`app/main.py`)
- ✅ Added support for multiple Bland AI payload formats (inbound + outbound)
- ✅ Added comprehensive logging of full webhook payloads
- ✅ Added catch-all endpoint to detect webhooks sent to wrong paths
- ✅ Better error handling and debugging info

### 2. Updated Inbound Configuration
- ✅ Added `webhook_events` to configuration (though Bland returned empty array)
- ✅ Added tools array with all 4 custom tools
- ✅ Updated prompt to instruct agent to use the tools

### 3. Created Diagnostic Scripts
- `scripts/check_inbound_config.py` - View current Bland inbound configuration
- `scripts/update_inbound_webhook.py` - Update webhook URL and settings
- `scripts/check_webhook_logs.py` - Check server logs for webhook activity
- `scripts/test_webhook.py` - Test webhook locally (WORKS ✅)

## Next Steps to Fix

### Option 1: Verify ngrok URL is reachable (RECOMMENDED)
```bash
# Test if Bland can reach your ngrok URL
curl -X POST https://acerbic-madalynn-nonthoracic.ngrok-free.dev/webhooks/bland/test \\
  -H "Content-Type: application/json" \\
  -d '{"test": "data"}'
```

Check if this shows up in your server logs. If not, ngrok might have issues.

### Option 2: Check ngrok dashboard
Visit http://127.0.0.1:4040 and look at:
- **Status**: Should show "online"
- **Connections**: Check if any incoming requests from Bland (likely from AWS IPs)
- **Replay failed requests**: See if Bland tried but failed

### Option 3: Make a test call and monitor
1. Make sure server is running: `py -m uvicorn app.main:app --reload`
2. Open server logs: `C:\\Users\\avide\\.cursor\\projects\\c-Users-avide-Desktop-propvoice-mvp\\terminals\\180744.txt`
3. Open ngrok dashboard: http://127.0.0.1:4040
4. Call your number: **+16307963284**
5. Watch both logs in real-time

### Option 4: Use Bland's call logs
1. Go to https://app.bland.ai/dashboard
2. Click on "Phone Numbers" → Find +16307963284
3. Click "Call Logs" or "Recent Calls"
4. Check if webhooks were attempted and if there were any errors

### Option 5: Try webhook URL with trailing slash
Some APIs are sensitive to trailing slashes. Try updating to:
```
https://acerbic-madalynn-nonthoracic.ngrok-free.dev/webhooks/bland/call-ended/
```

## Testing Checklist

Before making a real call, verify:
- [ ] Server is running on port 8000
- [ ] ngrok is running and forwarding to localhost:8000
- [ ] ngrok URL matches the one in `.env` and Bland configuration
- [ ] No firewall blocking port 8000
- [ ] Server logs show startup message

## Known Working Test

Run this to confirm everything works locally:
```bash
cd c:\\Users\\avide\\Desktop\\propvoice_mvp
py scripts/test_webhook.py
```

Expected result:
- ✅ Call saved to Supabase
- ✅ Email summary generated and sent
- ✅ Status 200 response

## If Webhooks Still Don't Work

The issue is likely one of these:

1. **Bland doesn't support webhooks for free trial numbers**
   - Check your Bland account plan
   - Contact Bland support to enable webhooks

2. **Ngrok free tier limitations**
   - ngrok free tier might timeout or rate-limit
   - Consider upgrading to ngrok Basic ($8/month)

3. **Bland API limitation**
   - `webhook_events: []` suggests feature might not be enabled
   - May need to contact Bland support

## Alternative: Poll Bland's API Instead

If webhooks can't work, you can poll Bland's API for completed calls:

```python
# scripts/poll_bland_calls.py
import requests
import time

while True:
    # Get recent calls
    response = requests.get(
        "https://api.bland.ai/v1/calls",
        headers={"Authorization": BLAND_API_KEY}
    )
    
    # Process new calls
    # ...
    
    time.sleep(60)  # Check every minute
```

## Summary

Your integration is **fully functional** when tested locally. The issue is specifically with **Bland AI not sending webhooks** after real inbound calls. This is an external integration issue, not a code issue.

The most likely causes are:
1. Ngrok URL not reachable from Bland's servers
2. Bland's webhook feature not enabled for your account/number
3. Configuration issue in Bland's system (empty `webhook_events` array)

**Recommendation**: Contact Bland support and share:
- Your phone number: +16307963284
- Your webhook URL: https://acerbic-madalynn-nonthoracic.ngrok-free.dev/webhooks/bland/call-ended
- The fact that `webhook_events` returns empty array
- Ask them to enable webhooks for inbound calls
