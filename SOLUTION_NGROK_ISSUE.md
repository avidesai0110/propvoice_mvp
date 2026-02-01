# SOLUTION: ngrok Free Tier Blocking Webhooks

## The Problem

ngrok's free tier shows an **interstitial warning page** before allowing access to your app. This blocks automated webhook requests from Bland AI.

When Bland tries to send a webhook, it gets HTML instead of reaching your FastAPI server:
```
"You are about to visit acerbic-madalynn-nonthoracic.ngrok-free.dev... 
You should only visit this website if you trust whoever sent the link to you."
```

## Solutions (Choose ONE)

### Option 1: Upgrade to ngrok Basic Plan ($8/month) ⭐ RECOMMENDED
This removes the warning page and enables webhooks to work properly.

1. Go to: https://dashboard.ngrok.com/billing/subscription
2. Upgrade to Basic plan
3. Restart ngrok
4. Test webhook again

**Benefits:**
- No warning page
- Reserved domain (keeps same URL)
- Better for production use

### Option 2: Use a Free Alternative to ngrok

**A) LocalTunnel** (Free, No Warning Page)
```bash
# Install
npm install -g localtunnel

# Start tunnel
lt --port 8000 --subdomain propvoice
# URL: https://propvoice.loca.lt
```

Then update `.env`:
```bash
API_BASE_URL=https://propvoice.loca.lt
```

And update Bland inbound number:
```bash
cd c:\\Users\\avide\\Desktop\\propvoice_mvp
py scripts/update_inbound_webhook.py
```

**B) Cloudflare Tunnel** (Free, No Warning Page)
```bash
# Download: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/

# Start tunnel
cloudflared tunnel --url http://localhost:8000
```

**C) serveo** (Free, SSH-based)
```bash
ssh -R 80:localhost:8000 serveo.net
```

### Option 3: Deploy to a Free Cloud Service

**A) Railway.app** (Free tier available)
1. Go to: https://railway.app
2. Connect your GitHub repo
3. Deploy automatically
4. Get a permanent URL (e.g., `https://propvoice-production.up.railway.app`)

**B) Render.com** (Free tier available)
1. Go to: https://render.com
2. New Web Service → Connect repo
3. Free tier includes HTTPS
4. Get URL: `https://propvoice.onrender.com`

**C) Fly.io** (Free tier available)
```bash
# Install flyctl
# In your project directory:
fly launch
fly deploy
```

## Quick Fix: Use LocalTunnel (5 minutes)

1. Install Node.js if not installed: https://nodejs.org

2. Install LocalTunnel:
```bash
npm install -g localtunnel
```

3. Start LocalTunnel (keep ngrok running or stop it):
```bash
lt --port 8000
```

4. Copy the URL it gives you (e.g., `https://empty-owls-warn.loca.lt`)

5. Update your `.env`:
```
API_BASE_URL=https://empty-owls-warn.loca.lt
```

6. Update Bland configuration:
```bash
cd c:\\Users\\avide\\Desktop\\propvoice_mvp
py scripts/update_inbound_webhook.py
```

7. Make a test call to +16307963284

8. Check server logs for incoming webhook

## Verification After Fix

After switching away from ngrok free or upgrading, test:

```bash
# Should return JSON, not HTML
Invoke-RestMethod -Uri "https://YOUR-NEW-URL/webhooks/bland/call-ended" -Method POST -Body '{"test":"data"}' -ContentType "application/json"
```

You should see JSON response like:
```json
{"status": "error", "message": "..."}
```

NOT HTML with "You are about to visit..."

## Why This Happened

- ngrok free tier: Shows warning page for ALL HTTP requests
- Bland AI webhooks: Automated POST requests
- Result: Bland gets HTML warning page instead of your API
- Your server: Never receives the webhook

## Next Steps

1. Choose a solution above
2. Update `API_BASE_URL` in `.env`
3. Run `py scripts/update_inbound_webhook.py`
4. Make a test call
5. Check `TROUBLESHOOTING_WEBHOOKS.md` for verification steps

Your code is correct - it's just the ngrok free tier blocking external webhooks!
