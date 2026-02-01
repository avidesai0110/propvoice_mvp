# 🚀 Quick Start Guide - Property Voice Agent

## Prerequisites
- Python 3.12+ installed
- Node.js installed (for LocalTunnel)
- All dependencies installed (`pip install -r requirements.txt`)
- `.env` file configured with your API keys

## Starting the Server

### 1. Start FastAPI Server
Open a terminal and run:
```bash
cd c:\Users\avide\Desktop\propvoice_mvp
py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Keep this terminal open** - the server needs to stay running.

### 2. Start LocalTunnel (in a separate terminal)
Open a **new terminal** and run:
```bash
cd c:\Users\avide\Desktop\propvoice_mvp
lt --port 8000
```

**Copy the URL** it gives you (e.g., `https://random-name.loca.lt`)

**Keep this terminal open** - LocalTunnel needs to stay running.

### 3. Update API Base URL
If LocalTunnel gives you a new URL, update your `.env` file:
```bash
py scripts/update_api_url.py https://YOUR-LOCALTUNNEL-URL
```

### 4. Update Bland AI Webhook
Update your Bland AI inbound number with the new webhook URL:
```bash
py scripts/update_inbound_webhook.py
```

## Verification

### Check Server Health
```bash
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
```

Should return:
```json
{
  "status": "healthy",
  "property": "Desai Property"
}
```

### Check LocalTunnel
```bash
Invoke-RestMethod -Uri "https://YOUR-LOCALTUNNEL-URL/health" -Method GET
```

Should return the same JSON response.

## Testing

### Test Webhook Locally
```bash
py scripts/test_webhook.py
```

Should save a test call to Supabase and send an email.

### Test Real Call
Call your Bland AI number: **+16307963284**

Then check:
1. **Server logs** - Should show webhook received
2. **Supabase** - Check `calls` table for new record
3. **Email** - Check for call summary email

## Monitoring Logs

### Watch Server Logs
```bash
Get-Content "C:\Users\avide\.cursor\projects\c-Users-avide-Desktop-propvoice-mvp\terminals\180744.txt" -Tail 20 -Wait
```

### Watch LocalTunnel Logs
```bash
Get-Content "C:\Users\avide\.cursor\projects\c-Users-avide-Desktop-propvoice-mvp\terminals\348837.txt" -Tail 20 -Wait
```

## Troubleshooting

### Server won't start - Port 8000 in use
Find and kill the process:
```bash
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

### LocalTunnel not working
Restart it:
```bash
# Press Ctrl+C to stop LocalTunnel
lt --port 8000
# Copy new URL and update .env + Bland AI config
```

### Webhooks not received
1. Check server is running on port 8000
2. Check LocalTunnel is running and forwarding
3. Check Bland AI webhook URL is correct: `py scripts/check_inbound_config.py`
4. Make a test call and watch server logs

## Quick Restart

If you need to restart everything:

```bash
# Terminal 1: Restart FastAPI
# Press Ctrl+C, then:
py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Restart LocalTunnel
# Press Ctrl+C, then:
lt --port 8000
# Update .env and Bland AI if URL changed
```

## Environment Variables

Make sure your `.env` has:
```
BLAND_API_KEY=your_bland_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
RESEND_API_KEY=your_resend_api_key
OPENAI_API_KEY=your_openai_api_key
MANAGER_EMAIL=your@email.com
API_BASE_URL=https://your-localtunnel-url.loca.lt
PROPERTY_NAME=Desai Property
DEBUG=true
```

## Production Deployment

For production, replace LocalTunnel with a permanent solution:
- **ngrok Basic** ($8/month) - Easiest upgrade
- **Railway.app** - Free tier, permanent URL
- **Render.com** - Free tier, permanent URL
- **Fly.io** - Free tier, global deployment

See `SOLUTION_NGROK_ISSUE.md` for detailed deployment options.

---

**Your Bland AI Number**: +16307963284  
**Webhook Endpoint**: `{API_BASE_URL}/webhooks/bland/call-ended`
