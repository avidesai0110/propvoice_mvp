# 🏠 Property Voice Agent MVP

AI-powered voice agent for property management using Bland AI, Supabase, and FastAPI.

## Features

- 📞 **24/7 AI Voice Agent** - Handles leasing, maintenance, and payment calls
- 🔧 **Automated Ticket Creation** - Creates maintenance tickets during calls
- 📅 **Tour Scheduling** - Books property tours for prospective tenants
- 📧 **Email Summaries** - AI-generated call summaries sent to property managers
- 🗄️ **Full Call Logging** - Records, transcripts, and analytics in Supabase

## Quick Start

### Prerequisites

- Python 3.9+
- Accounts on: [Bland AI](https://bland.ai), [Supabase](https://supabase.com), [Resend](https://resend.com), [OpenAI](https://platform.openai.com)

### 1. Clone and Install

```bash
cd propvoice_mvp
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
copy .env.example .env
# Edit .env with your API keys
```

### 3. Set Up Supabase

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to SQL Editor
3. Copy contents of `database/schema.sql` and run it
4. Copy your project URL and anon key to `.env`

### 4. Seed Test Data

```bash
python scripts/seed_data.py
```

### 5. Run the Server

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Expose with ngrok (for local testing)

```bash
ngrok http 8000
# Copy the https URL to .env as API_BASE_URL
```

### 7. Create Bland AI Agent

```bash
python scripts/create_bland_agent.py --create
```

## Project Structure

```
propvoice_mvp/
├── app/
│   ├── __init__.py
│   ├── config.py           # Settings & environment
│   ├── main.py             # FastAPI application
│   └── services/
│       ├── database.py     # Supabase operations
│       ├── email.py        # Resend email service
│       └── summary.py      # OpenAI summaries
├── database/
│   └── schema.sql          # Supabase schema
├── scripts/
│   ├── create_bland_agent.py
│   └── seed_data.py
├── .env.example
├── requirements.txt
└── README.md
```

## API Endpoints

### Tools (Called by Bland AI during calls)

| Endpoint | Description |
|----------|-------------|
| `POST /tools/check-availability` | Query available units |
| `POST /tools/create-ticket` | Create maintenance ticket |
| `POST /tools/schedule-tour` | Schedule property tour |
| `POST /tools/get-payment-info` | Get payment information |

### Webhooks

| Endpoint | Description |
|----------|-------------|
| `POST /webhooks/bland/call-ended` | Process completed calls |

### Health

| Endpoint | Description |
|----------|-------------|
| `GET /` | API info |
| `GET /health` | Health check |

## Configuration

| Variable | Description |
|----------|-------------|
| `BLAND_API_KEY` | Bland AI API key |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase anon/service key |
| `RESEND_API_KEY` | Resend email API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `MANAGER_EMAIL` | Email for call summaries |
| `API_BASE_URL` | Your deployed API URL |
| `PROPERTY_NAME` | Property name for agent |

## Deployment

### Railway (Recommended)

1. Push code to GitHub
2. Connect Railway to your repo
3. Add environment variables
4. Deploy!

### Render

1. Create new Web Service
2. Connect to GitHub repo
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables

## Testing

Call your Bland AI phone number and try:

- "I'm looking for a 2 bedroom apartment"
- "I need to report a maintenance issue in unit 101"
- "I'd like to schedule a tour"
- "How do I pay my rent?"

## License

MIT
