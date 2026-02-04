# 🏢 AI COMPANY Agent

**Complete multi-agent AI company running locally with Hugging Face (100% FREE!)**

No Azure, no OpenAI API costs - just your Hugging Face account (free tier works great!)

---

## 🎯 What You Get

**6 Specialist AI Agents:**
- 👔 **HR Manager** - Routes queries, schedules interviews, manages recruitment
- 🛠️ **AI Engineer** - Builds AI agents, generates code, creates automation
- 📊 **Data Analyst** - ETL pipelines, SQL queries, visualizations
- 📋 **PMO/Scrum Master** - Project tracking, standups, status reports
- 🔒 **Security Pentester** - Vulnerability scanning, security audits
- 🚀 **DevOps Engineer** - CI/CD pipelines, infrastructure deployment

**Two Ways to Use:**
1. **FastAPI Server** - RESTful API endpoints (production-ready)
2. **Local Testing** - Interactive command-line interface (testing & development)

**Special Features:**
- ✅ Code generation with approval workflow
- ✅ Local vector memory (ChromaDB)
- ✅ Conversation history
- ✅ Multi-agent collaboration
- ✅ 100% free and open source

---

## 🚀 QUICK START (5 Minutes)

### Step 1: Get Hugging Face API Key (FREE)

1. Go to https://huggingface.co/
2. Sign up (free)
3. Go to https://huggingface.co/settings/tokens
4. Click "New token"
5. Give it a name (e.g., "ai-company")
6. Select "Read" access
7. Click "Generate"
8. **Copy the token** (starts with `hf_`)

### Step 2: Install

```bash
# Clone or download this project
cd local_ai_company

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure

```bash
# Create .env file
cp .env.template .env

# Edit .env and add your Hugging Face token:
# HUGGINGFACE_API_KEY=hf_your_token_here
```

### Step 4: Test It!

```bash
# Run local test (interactive mode)
python test_local.py

# Choose option 2 for interactive chat
# Then try: "Build me a customer support AI agent"
```

### Step 5: Start API Server (Optional)

```bash
# Start the FastAPI server
python api_server.py

# Open browser to http://localhost:8000/docs
# Try the /query endpoint with:
# {
#   "query": "Schedule interviews for 3 AI engineers"
# }
```

---

## 📋 DETAILED SETUP

### Prerequisites

- **Python 3.9+** (3.11 recommended)
- **Hugging Face account** (free)
- **4GB RAM minimum** (8GB recommended)
- **Internet connection** (for Hugging Face API)

### Installation

```bash
# 1. Create project directory
mkdir ai_company
cd ai_company

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cat > .env << EOF
HUGGINGFACE_API_KEY=hf_your_token_here
HF_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2
API_HOST=0.0.0.0
API_PORT=8000
MEMORY_PERSIST_DIRECTORY=./data/memory
AGENT_CODE_WORKSPACE=./agent_workspace
AGENT_CODE_PENDING=./agent_workspace/pending_approval
AGENT_CODE_APPROVED=./agent_workspace/approved
LOG_LEVEL=INFO
EOF

# 5. Create necessary directories
mkdir -p data/memory
mkdir -p agent_workspace/pending_approval
mkdir -p agent_workspace/approved
```

---

## 🎮 USAGE

### Option 1: Local Testing (Best for Development)

```bash
python test_local.py
```

**Features:**
- Interactive chat mode
- Run test scenarios
- Approve generated code
- View conversation history

**Example Queries:**
```
"Build me a chatbot for customer support"
"Analyze sales data and create visualizations"
"Schedule interviews for 5 data scientists"
"Run security scan on our web app"
"Deploy microservice to production"
```

### Option 2: API Server (Best for Production)

```bash
# Start server
python api_server.py

# Server runs on http://localhost:8000
```

**API Endpoints:**

1. **Submit Query**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Build me an AI agent for email automation",
    "session_id": "my_session_001"
  }'
```

2. **Check Pending Code**
```bash
curl http://localhost:8000/pending-code
```

3. **Approve Code**
```bash
curl -X POST http://localhost:8000/approve-code \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "email_automation_agent.py",
    "approved": true
  }'
```

4. **Get Conversation History**
```bash
curl http://localhost:8000/history/my_session_001
```

5. **API Documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🧪 TESTING EXAMPLES

### Test 1: Build an AI Agent

```python
# In test_local.py or via API
query = """
Build me a customer support AI agent that can:
1. Answer FAQs from a knowledge base
2. Create Jira tickets for complex issues
3. Escalate to human agents when needed
"""
```

**What happens:**
1. HR Agent routes to AI Engineer
2. AI Engineer generates complete Python code
3. Code is saved to `./agent_workspace/pending_approval/`
4. You review and approve the code
5. Approved code moves to `./agent_workspace/approved/`

### Test 2: Data Analysis

```python
query = """
Analyze our Q4 sales data:
1. Extract data from SQL database
2. Calculate growth rates by region
3. Create visualizations (bar charts, trend lines)
4. Generate executive summary report
"""
```

**What happens:**
1. HR Agent routes to Data Analyst
2. Data Analyst generates SQL queries and Python code
3. Creates mock visualizations
4. Provides analysis summary

### Test 3: Multi-Agent Workflow

```python
query = """
End-to-end deployment:
1. Build a new microservice for user authentication
2. Run security tests
3. Create CI/CD pipeline
4. Deploy to production
5. Track project in Jira
"""
```

**What happens:**
1. HR Agent creates execution plan
2. AI Engineer builds the microservice
3. Security Agent runs vulnerability scans
4. DevOps Agent creates CI/CD pipeline
5. PMO Agent updates project tracker

---

## 📁 PROJECT STRUCTURE

```
local_ai_company/
├── api_server.py              # FastAPI server
├── test_local.py              # Local testing script
├── requirements.txt           # Python dependencies
├── .env                       # Configuration (YOU CREATE THIS)
├── .env.template              # Template for .env
├── src/
│   ├── llm_config.py          # Hugging Face LLM setup
│   ├── memory_manager.py      # ChromaDB vector memory
│   └── agents.py              # All 6 agents (CrewAI)
├── data/
│   └── memory/                # ChromaDB storage (auto-created)
└── agent_workspace/
    ├── pending_approval/      # Generated code awaiting review
    └── approved/              # Approved code
```

---

## 🔧 CONFIGURATION

### Environment Variables (.env)

```bash
# Required
HUGGINGFACE_API_KEY=hf_xxxxx  # Get from huggingface.co/settings/tokens

# Optional (defaults provided)
HF_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2
API_HOST=0.0.0.0
API_PORT=8000
MEMORY_PERSIST_DIRECTORY=./data/memory
AGENT_CODE_WORKSPACE=./agent_workspace
AGENT_CODE_PENDING=./agent_workspace/pending_approval
AGENT_CODE_APPROVED=./agent_workspace/approved
LOG_LEVEL=INFO
```

### Recommended Free Models

```python
# Mistral 7B - Best quality (recommended)
HF_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2

# TinyLlama - Fastest (good for testing)
HF_MODEL_NAME=TinyLlama/TinyLlama-1.1B-Chat-v1.0

# FLAN-T5 - Good balance
HF_MODEL_NAME=google/flan-t5-large

# Zephyr 7B - High quality
HF_MODEL_NAME=HuggingFaceH4/zephyr-7b-beta
```

---

## 💡 HOW IT WORKS

### Agent Flow

```
User Query
    ↓
HR Agent (Orchestrator)
    ↓
Analyzes query and routes to specialists
    ↓
    ├─→ AI Engineer (for code/agent tasks)
    ├─→ Data Analyst (for data tasks)
    ├─→ PMO (for project management)
    ├─→ Security (for security tasks)
    └─→ DevOps (for infrastructure tasks)
    ↓
Agents collaborate using CrewAI
    ↓
Results returned to user
```

### Code Approval Workflow

```
1. AI Engineer generates code
   ↓
2. Code saved to ./agent_workspace/pending_approval/
   ↓
3. User reviews code via:
   - test_local.py (type "approve code")
   - API endpoint (/pending-code, /approve-code)
   ↓
4a. APPROVED → moves to ./agent_workspace/approved/
4b. REJECTED → deleted
   ↓
5. Approved code ready to use!
```

### Memory System

- **ChromaDB** - Local vector database (no cloud needed)
- **Conversations** - Stored with session IDs
- **Knowledge Base** - Agent-generated knowledge
- **Project History** - Track ongoing work
- **Agent Outputs** - Code and results

---

## 🚨 TROUBLESHOOTING

### Issue: "HUGGINGFACE_API_KEY not found"

**Solution:**
```bash
# Make sure .env file exists
ls -la .env

# Check contents
cat .env

# Should contain:
# HUGGINGFACE_API_KEY=hf_your_actual_token_here
```

### Issue: "Model loading takes forever"

**Solution:**
Try a smaller/faster model:
```bash
# In .env:
HF_MODEL_NAME=TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

### Issue: "Rate limit exceeded"

**Solution:**
Hugging Face free tier has rate limits. Wait a minute and try again, or:
- Upgrade to Hugging Face Pro ($9/month)
- Use a smaller model (fewer API calls)

### Issue: "Import errors"

**Solution:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Or install individually:
pip install crewai crewai-tools langchain langchain-community
pip install fastapi uvicorn chromadb python-dotenv rich
```

### Issue: "API server won't start"

**Solution:**
```bash
# Check if port is in use
netstat -an | grep 8000

# Use different port:
export API_PORT=8001
python api_server.py
```

---

## 📊 PERFORMANCE TIPS

### Speed Up Responses

1. **Use smaller model:**
   ```bash
   HF_MODEL_NAME=TinyLlama/TinyLlama-1.1B-Chat-v1.0
   ```

2. **Reduce max_length:**
   Edit `src/llm_config.py`:
   ```python
   max_length=1024  # Instead of 2048
   ```

3. **Simplify queries:**
   Be specific and concise in your requests

### Improve Quality

1. **Use larger model:**
   ```bash
   HF_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2
   ```

2. **Provide more context:**
   Include relevant details in your queries

3. **Adjust temperature:**
   Edit `src/llm_config.py` role-specific temperatures

---

## 🔒 SECURITY NOTES

- **API Key Safety:** Never commit .env to git (it's in .gitignore)
- **Local Only:** This setup runs locally - no data sent to cloud
- **Code Review:** Always review AI-generated code before using
- **Network Security:** API server binds to 0.0.0.0 - restrict in production

---

## 🆘 NEED HELP?

### Common Questions

**Q: Do I need Azure/OpenAI?**
A: No! This is 100% free using Hugging Face.

**Q: What's the cost?**
A: Free! Hugging Face free tier works great.

**Q: How do I approve code?**
A: Run `test_local.py` and choose option 3, or use API endpoint `/approve-code`

**Q: Can I use my own LLM?**
A: Yes! Edit `src/llm_config.py` and modify the `get_llm()` function

**Q: Does it work offline?**
A: No - needs internet for Hugging Face API calls

---

## 📝 EXAMPLE SESSION

```bash
$ python test_local.py

╔══════════════════════════════════════════════════════════════╗
║        🏢 AI COMPANY - LOCAL TEST ENVIRONMENT                ║
╚══════════════════════════════════════════════════════════════╝

✅ Hugging Face API key found
✅ AI Company initialized successfully!

Choose an option:
  1. Run all test scenarios
  2. Interactive mode
  3. Approve pending code
  4. Quick single test

Your choice [2]:

💬 INTERACTIVE MODE

You: Build me a todo list app with AI prioritization

Processing...

🤖 AI Company:
I'll help you build a todo list app with AI prioritization. Let me break this down:

1. AI Engineer will create the app code
2. Security will review for vulnerabilities
3. DevOps will set up deployment

[AI Engineer generates code...]
✅ Code saved to: ./agent_workspace/pending_approval/todo_app.py

You: approve code

📁 Found 1 file(s) pending approval

File: todo_app.py
Description: AI-powered todo list application

[Code displayed with syntax highlighting]

Approve this code? [y/n]: y

✅ Code approved and saved to: ./agent_workspace/approved/todo_app.py
```

---

## 🎉 YOU'RE READY!

Start with:
```bash
python test_local.py
```

Try queries like:
- "Build me a chatbot"
- "Analyze this data: [paste data]"
- "Schedule 5 interviews next week"
- "Run security audit"
- "Deploy to production"

Have fun with your AI company! 🚀
