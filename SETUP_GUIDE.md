# AI Company - Complete Setup Guide

This guide covers setting up **Supabase**, **SMTP (Gmail)**, and **Google Calendar API** for the AI Company multi-agent system.

---

## Quick Start

```bash
# 1. Run the test to see what needs configuration
python test_complete.py

# 2. After configuring .env, run tests again
python test_complete.py

# 3. Start the API server
python api_server.py

# 4. Access API docs at http://localhost:8000/docs
```

---

## 1. Supabase Setup (FREE - 5 minutes)

### What You Get (Free Tier)
- 500MB PostgreSQL database
- 1GB file storage
- 50,000 monthly active users
- Unlimited API requests
- 2 projects

### Step-by-Step Setup

#### Step 1: Create Account
1. Go to [https://supabase.com](https://supabase.com)
2. Click **"Start your project"**
3. Sign up with **GitHub** (recommended) or **Email**

#### Step 2: Create Project
1. Click **"New Project"**
2. Fill in:
   - **Name:** `ai-company` (or any name)
   - **Database Password:** Create a strong password (SAVE THIS!)
   - **Region:** Choose closest to you
3. Click **"Create new project"**
4. Wait 2-3 minutes for setup

#### Step 3: Get API Keys
1. Go to **Settings** (gear icon) → **API**
2. Copy these values:

```
Project URL:     https://xxxxx.supabase.co
anon/public:     eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
service_role:    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Step 4: Update .env
```env
# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # anon key
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6...  # service_role key
DB_PROVIDER=supabase
```

#### Step 5: Verify
```bash
python test_complete.py
# Look for "DATABASE CONNECTION" section - should show PASS
```

---

## 2. Gmail SMTP Setup (FREE - 3 minutes)

### What You Get
- Send up to 500 emails/day
- Works with any Gmail account
- No credit card required

### Step-by-Step Setup

#### Step 1: Enable 2-Step Verification
1. Go to [https://myaccount.google.com](https://myaccount.google.com)
2. Click **Security** (left sidebar)
3. Under "Signing in to Google", click **2-Step Verification**
4. Click **Get Started** and follow the prompts
5. Complete setup with phone number

#### Step 2: Create App Password
1. Go to [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - If you don't see this option, 2-Step Verification isn't enabled
2. Click **Select app** → Choose **Mail**
3. Click **Select device** → Choose **Other (Custom name)**
4. Enter: `AI Company Agent`
5. Click **Generate**
6. **Copy the 16-character password** (looks like: `xxxx xxxx xxxx xxxx`)

#### Step 3: Update .env
```env
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-actual-email@gmail.com
SMTP_PASSWORD=xxxxxxxxxxxxxxxx   # 16-char password, no spaces
```

#### Step 4: Verify
```bash
python test_complete.py
# Look for "SMTP EMAIL" section - should show PASS
```

### Troubleshooting
- **"Less secure app access"** - Not needed with App Passwords
- **"Authentication failed"** - Make sure you copied the App Password correctly (no spaces)
- **"2-Step Verification required"** - Complete Step 1 first

---

## 3. Google Calendar API Setup (FREE - 10 minutes)

### What You Get
- Create/read/update calendar events
- Send calendar invites
- Works with personal or workspace accounts

### Option A: Simple ICS Files (No Setup Required!)

The system already generates `.ics` files that work with ANY calendar:
- Double-click to add to Google Calendar, Outlook, Apple Calendar
- No API setup needed
- Files saved in: `agent_workspace/pmo/meetings/`

**If this is sufficient, skip to the next section!**

### Option B: Full Google Calendar API

#### Step 1: Create Google Cloud Project
1. Go to [https://console.cloud.google.com](https://console.cloud.google.com)
2. Click **Select a project** (top bar) → **New Project**
3. Name: `AI Company` → Click **Create**
4. Wait for project creation

#### Step 2: Enable Calendar API
1. Go to **APIs & Services** → **Library**
2. Search for **"Google Calendar API"**
3. Click on it → Click **Enable**

#### Step 3: Create OAuth Credentials
1. Go to **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **OAuth client ID**
3. If prompted, configure **OAuth consent screen**:
   - User Type: **External** → Create
   - App name: `AI Company`
   - User support email: Your email
   - Developer contact: Your email
   - Click **Save and Continue** through all steps
4. Back to Credentials → **+ Create Credentials** → **OAuth client ID**
5. Application type: **Desktop app**
6. Name: `AI Company Desktop`
7. Click **Create**
8. Click **Download JSON**
9. Save as `credentials.json` in project root

#### Step 4: Update .env
```env
# Google Calendar Configuration
GOOGLE_CALENDAR_CREDENTIALS=./credentials.json
GOOGLE_CALENDAR_TOKEN=./token.json
```

#### Step 5: First-Time Authorization
```bash
python -c "from src.adk.tools import get_calendar_service; get_calendar_service()"
```
- A browser window will open
- Sign in with your Google account
- Click **Allow**
- A `token.json` file will be created

#### Step 6: Verify
```bash
python test_complete.py
# Look for "CALENDAR" section - should show PASS
```

---

## 4. Verify All Services

Run the complete test suite:

```bash
python test_complete.py
```

Expected output:
```
╔══════════════════════════════════════════════════════════════╗
║     AI COMPANY - COMPREHENSIVE TEST SUITE                    ║
╚══════════════════════════════════════════════════════════════╝

1. ENVIRONMENT CONFIGURATION
  [PASS] MODEL_PROVIDER = huggingface
  [PASS] HUGGINGFACE_API_KEY = hf_CnAo...
  [PASS] SUPABASE_URL: configured
  [PASS] SMTP_USER: configured

2. DATABASE CONNECTION
  [PASS] Database Provider: supabase
  [PASS] Test Query
  [PASS] CREATE TABLE
  [PASS] INSERT
  [PASS] SELECT
  [PASS] DELETE

3. SMTP EMAIL
  [PASS] SMTP Host: smtp.gmail.com
  [PASS] SMTP Login

4. CALENDAR (ICS Generation)
  [PASS] Meeting Created
  [PASS] ICS File Generated

...

TEST SUMMARY
  ENVIRONMENT          [PASS] 4/4 tests
  DATABASE             [PASS] 6/6 tests
  SMTP                 [PASS] 2/2 tests
  CALENDAR             [PASS] 4/4 tests
  HR_MANAGER           [PASS] 3/3 tests
  PMO                  [PASS] 3/3 tests
  SECURITY             [PASS] 4/4 tests
  DATA_ANALYST         [PASS] 5/5 tests
  API                  [PASS] 7/7 tests

TOTAL: 38 passed, 0 failed

All tests passed! System is ready.
```

---

## 5. Start the API Server

```bash
python api_server.py
```

Access:
- **API Documentation:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## API Endpoints Reference

### Core Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| POST | `/query` | Submit query to agents |
| GET | `/agents/list` | List all agents |

### HR Manager
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/hr/search-candidates` | Search for candidates |
| POST | `/hr/onboard` | Start onboarding |
| GET | `/hr/employees` | List employees |

### PMO/Scrum Master
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/pmo/tasks` | Create task |
| GET | `/pmo/tasks` | List tasks |
| POST | `/pmo/meetings` | Schedule meeting |
| GET | `/pmo/meetings/{id}/ics` | Download ICS file |
| POST | `/pmo/excel-tracker` | Create Excel tracker |

### Security Pentester
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/security/pentest/session` | Create pentest session |
| POST | `/security/pentest/scan` | Run security scan |
| GET | `/security/pentest/{id}/results` | Get results |
| GET | `/security/pentest/{id}/report` | Generate report |

### Data Analyst
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/data/ingest` | Ingest data file |
| POST | `/data/query` | Query data (SQL/RAG) |
| GET | `/data/catalog` | Get data catalog |
| POST | `/data/chart` | Create chart |
| POST | `/data/dashboard` | Create dashboard |

### Database
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/db/status` | Database status |
| GET | `/db/schema` | Database schema |
| POST | `/email/test` | Test email sending |

---

## Troubleshooting

### Supabase Issues
- **"Connection refused"** - Check SUPABASE_URL is correct
- **"Invalid API key"** - Use the `anon` key, not `service_role`
- **"Permission denied"** - Check Row Level Security policies

### SMTP Issues
- **"Authentication failed"** - Regenerate App Password
- **"Connection timeout"** - Check firewall/antivirus
- **"SMTP not supported"** - Use port 587 with TLS

### Calendar Issues
- **"credentials.json not found"** - Download from Google Cloud Console
- **"Access denied"** - Re-run authorization flow
- **"Quota exceeded"** - Wait 24 hours (free tier limits)

---

## Support

- Check logs in `agent_workspace/logs/`
- Run `python test_complete.py` for diagnostics
- All tools are FREE and open-source
