# 🏢 AI Company - Complete Multi-Agent System

## 📖 ELABORATE WORKING DOCUMENTATION

**A comprehensive guide to understanding and using the AI Company system - explained for beginners and experts alike.**

---

## 🎯 What is the AI Company?

Imagine a virtual company where AI agents work together like real employees to handle complex tasks. This system creates **6 specialized AI agents** that collaborate to solve problems, just like a real company's team would.

**Key Features:**

- ✅ **6 Specialist AI Agents** working together
- ✅ **Real Database Integration** (SQLite)
- ✅ **File System Access** for reading/writing files
- ✅ **External Tool Integration** (Jira, Email, GitHub, etc.)
- ✅ **Memory System** (remembers conversations)
- ✅ **Code Generation & Approval** workflow
- ✅ **REST API** for external access
- ✅ **100% Free** (uses Hugging Face)

---

## 🏗️ SYSTEM ARCHITECTURE

### How It All Works Together

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  HR Manager     │───▶│  Route to       │
│                 │    │  (Orchestrator) │    │  Specialists    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                    ┌──────────────────────────────────┼──────────────────────────────────┐
                    │                                  │                                  │
            ┌───────▼──────┐                   ┌───────▼──────┐                   ┌───────▼──────┐
            │ AI Engineer  │                   │ Data Analyst │                   │ Security     │
            │ - Code Gen   │                   │ - SQL/ETL    │                   │ - Penetration │
            │ - Automation │                   │ - Reports    │                   │ - Scanning    │
            └──────────────┘                   └──────────────┘                   └──────────────┘
                    │                                  │                                  │
            ┌───────▼──────┐                   ┌───────▼──────┐                   ┌───────▼──────┐
            │    PMO       │                   │   DevOps     │                   │   Memory     │
            │ - Project Mgmt│                   │ - CI/CD      │                   │   System     │
            │ - Jira       │                   │ - Deploy      │                   │   (ChromaDB) │
            └──────────────┘                   └──────────────┘                   └──────────────┘
                                                       │
                    ┌──────────────────────────────────┼──────────────────────────────────┐
                    │                                  │                                  │
            ┌───────▼──────┐                   ┌───────▼──────┐                   ┌───────▼──────┐
            │   Database   │                   │  File System │                   │  External     │
            │   (SQLite)   │                   │   Access     │                   │   APIs        │
            └──────────────┘                   └──────────────┘                   └──────────────┘
```

---

## 🤖 THE 6 AI AGENTS - DETAILED BREAKDOWN

### Agent Functionality Table

| Agent Role                        | Primary Function                    | Key Skills                                       | Tools Used                                  | Example Tasks                                             |
| --------------------------------- | ----------------------------------- | ------------------------------------------------ | ------------------------------------------- | --------------------------------------------------------- |
| **HR Manager**<br/>(Orchestrator) | Routes queries and coordinates team | Query analysis, task delegation, team management | Memory search, email, web search            | "Schedule interviews for 5 engineers" → Routes to PMO     |
| **AI Engineer**                   | Builds AI agents and automations    | Python coding, CrewAI, API development           | Code generation, file I/O, GitHub scanning  | "Build a chatbot" → Creates complete Python agent package |
| **Data Analyst**                  | Data processing and visualization   | SQL, ETL, pandas, matplotlib                     | Database queries, Excel R/W, visualization  | "Analyze sales data" → Creates reports and charts         |
| **PMO/Scrum Master**              | Project management and tracking     | Agile, Jira, status reporting                    | Jira tickets, email notifications, database | "Track project progress" → Updates Jira and sends reports |
| **Security Pentester**            | Security testing and auditing       | Penetration testing, vulnerability scanning      | Nmap, Nuclei, SQLMap, ZAP, Gobuster         | "Security audit website" → Runs multiple security scans   |
| **DevOps Engineer**               | Infrastructure and deployment       | CI/CD, Docker, Kubernetes, cloud                 | Infrastructure tools, deployment scripts    | "Deploy to production" → Creates CI/CD pipeline           |

### Agent Communication Flow

```
User Query → HR Manager analyzes → Routes to specialists → Agents collaborate → Results returned
```

---

## 🔧 MCP SERVERS - EXTERNAL TOOL INTEGRATION

### What is MCP (Model Context Protocol)?

MCP allows AI agents to access external tools and data sources safely. Think of it as "apps" that agents can use.

### MCP Servers Table

| MCP Server         | Purpose                        | Technologies      | Configuration Required                    | Status           |
| ------------------ | ------------------------------ | ----------------- | ----------------------------------------- | ---------------- |
| **Database MCP**   | SQL database access            | SQLite3, Python   | Auto-configured                           | ✅ Always Active |
| **Filesystem MCP** | File read/write operations     | Python pathlib    | Auto-configured                           | ✅ Always Active |
| **Jira MCP**       | Project management integration | Jira REST API     | JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN | ⚠️ Optional      |
| **Email MCP**      | Email sending capabilities     | SMTP              | SMTP_HOST, SMTP_USER, SMTP_PASSWORD       | ⚠️ Optional      |
| **GitHub MCP**     | Repository scanning            | GitHub API        | GITHUB_TOKEN                              | ⚠️ Optional      |
| **Excel MCP**      | Spreadsheet processing         | pandas, openpyxl  | Auto-configured                           | ✅ Always Active |
| **Web Search MCP** | Internet information gathering | SerpAPI           | SERP_API_KEY                              | ⚠️ Optional      |
| **Pentest MCP**    | Security testing tools         | Docker containers | Docker + pentest-mcp image                | ⚠️ Optional      |

### MCP Linkage Matrix

| Agent        | Database | Filesystem | Jira | Email | GitHub | Excel | Web Search | Pentest |
| ------------ | -------- | ---------- | ---- | ----- | ------ | ----- | ---------- | ------- |
| HR Manager   | ✅       | ❌         | ❌   | ✅    | ❌     | ❌    | ✅         | ❌      |
| AI Engineer  | ❌       | ✅         | ❌   | ❌    | ✅     | ❌    | ✅         | ❌      |
| Data Analyst | ✅       | ❌         | ❌   | ❌    | ❌     | ✅    | ❌         | ❌      |
| PMO          | ✅       | ❌         | ✅   | ✅    | ❌     | ❌    | ❌         | ❌      |
| Security     | ❌       | ✅         | ❌   | ❌    | ❌     | ❌    | ❌         | ✅      |
| DevOps       | ❌       | ✅         | ❌   | ❌    | ❌     | ❌    | ❌         | ❌      |

---

## 💾 DATABASE SYSTEM

### Database Schema

The system uses **SQLite** database (`company.db`) with the following tables:

#### Table: `employees`

| Column     | Type                | Description            |
| ---------- | ------------------- | ---------------------- |
| id         | INTEGER PRIMARY KEY | Unique employee ID     |
| name       | TEXT                | Employee full name     |
| role       | TEXT                | Job title/role         |
| email      | TEXT                | Email address          |
| department | TEXT                | Department name        |
| hire_date  | TEXT                | Hire date (YYYY-MM-DD) |

#### Table: `projects`

| Column     | Type                | Description                                 |
| ---------- | ------------------- | ------------------------------------------- |
| id         | INTEGER PRIMARY KEY | Unique project ID                           |
| name       | TEXT                | Project name                                |
| status     | TEXT                | Current status (active, completed, on-hold) |
| owner      | TEXT                | Project owner/manager                       |
| start_date | TEXT                | Start date (YYYY-MM-DD)                     |
| end_date   | TEXT                | End date (YYYY-MM-DD)                       |
| budget     | REAL                | Project budget                              |

#### Table: `tickets`

| Column      | Type                | Description                                  |
| ----------- | ------------------- | -------------------------------------------- |
| id          | INTEGER PRIMARY KEY | Unique ticket ID                             |
| title       | TEXT                | Ticket title                                 |
| description | TEXT                | Detailed description                         |
| status      | TEXT                | Status (open, in-progress, resolved, closed) |
| priority    | TEXT                | Priority level (low, medium, high, critical) |
| assignee    | TEXT                | Assigned person                              |
| created_at  | TEXT                | Creation timestamp                           |
| updated_at  | TEXT                | Last update timestamp                        |

### Database Operations

Agents can perform:

- **SELECT** queries to read data
- **INSERT/UPDATE/DELETE** for data modification
- **Schema inspection** to understand table structures

---

## 📁 FILE STRUCTURE - COMPLETE OVERVIEW

### Root Directory Structure

```
d:/DerivHack/
├── 📄 .env                    # Environment configuration
├── 📄 .env.template          # Configuration template
├── 📄 .gitignore             # Git ignore rules
├── 📄 README.md              # Basic documentation
├── 📄 ELABORATE_WORKING.md   # This detailed guide
├── 📄 requirements.txt       # Python dependencies
├── 📄 setup.sh               # Setup script
├── 📄 api_server.py         # FastAPI server
├── 📄 test_local.py          # Local testing interface
├── 📄 test_fix.py            # Testing utilities
├── 📄 test_agent_package.py  # Agent package testing
├── 📄 test_save_agent.py     # Agent saving tests
├── 📄 company.db             # SQLite database
├── 📁 venv/                  # Python virtual environment
├── 📁 src/                   # Source code
├── 📁 agent_workspace/       # Agent-generated content
└── 📁 data/                  # Data storage
```

### Source Code Structure (`src/`)

```
src/
├── 📄 __init__.py
├── 📄 agents.py              # All 6 agent definitions
├── 📄 llm_config.py          # Hugging Face LLM setup
├── 📄 memory_manager.py      # ChromaDB memory system
├── 📄 mcp_tools.py           # MCP server tools
├── 📄 pentest_mcp_tools.py   # Security testing tools
├── 📄 emergency.py           # Emergency handling
├── 📁 adk/                   # Google ADK integration
│   ├── 📄 __init__.py
│   ├── 📄 models.py          # Data models
│   ├── 📄 runner.py          # ADK runner
│   └── 📄 tools.py           # ADK tools
```

### Agent Workspace Structure (`agent_workspace/`)

```
agent_workspace/
├── 📁 pending_approval/      # Code awaiting review
│   ├── 📄 customer_support_agent.py
│   └── 📄 [other_agents].py
├── 📁 approved/              # Approved production code
│   ├── 📄 customer_support_agent.py
│   └── 📄 [other_agents].py
├── 📄 ci_cd_config.yml       # CI/CD configuration
└── 📄 web_application_security_report.txt
```

### Data Storage Structure (`data/`)

```
data/
└── 📁 memory/                # ChromaDB vector storage
    ├── 📁 [session_id_1]/    # Conversation memories
    ├── 📁 [session_id_2]/
    └── 📁 ...
```

---

## 🚀 INSTALLATION & SETUP

### Prerequisites

| Requirement          | Version  | Purpose         |
| -------------------- | -------- | --------------- |
| Python               | 3.9+     | Core runtime    |
| pip                  | Latest   | Package manager |
| Git                  | Latest   | Version control |
| Hugging Face Account | Free     | AI models       |
| SQLite3              | Built-in | Database        |

### Step-by-Step Installation

#### 1. Clone/Download Project

```bash
cd d:/DerivHack
# Project is already here
```

#### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure Environment

```bash
# Copy template
copy .env.template .env

# Edit .env file with your settings
notepad .env
```

#### 5. Get Hugging Face API Key

1. Go to https://huggingface.co/settings/tokens
2. Create new token (free)
3. Add to `.env`: `HUGGINGFACE_API_KEY=hf_your_token_here`

### Environment Variables

| Variable                 | Required | Default                            | Description             |
| ------------------------ | -------- | ---------------------------------- | ----------------------- |
| HUGGINGFACE_API_KEY      | ✅       | None                               | Hugging Face API token  |
| HF_MODEL_NAME            | ❌       | mistralai/Mistral-7B-Instruct-v0.2 | AI model to use         |
| API_HOST                 | ❌       | 0.0.0.0                            | API server host         |
| API_PORT                 | ❌       | 8000                               | API server port         |
| MEMORY_PERSIST_DIRECTORY | ❌       | ./data/memory                      | Memory storage location |
| AGENT_CODE_WORKSPACE     | ❌       | ./agent_workspace                  | Agent code workspace    |
| LOG_LEVEL                | ❌       | INFO                               | Logging level           |

---

## 🎮 USAGE MODES

### Mode 1: Local Testing (Interactive)

**Best for development and testing**

```bash
python test_local.py
```

**Features:**

- Interactive chat interface
- Test scenarios
- Code approval workflow
- Conversation history

**Example Session:**

```
Choose option: 2 (Interactive mode)

You: Build me a customer support chatbot

🤖 AI Company:
I'll route this to our AI Engineer...

[AI Engineer generates code...]
✅ Code saved to: ./agent_workspace/pending_approval/chatbot.py

You: approve code
✅ Code approved and moved to ./agent_workspace/approved/
```

### Mode 2: API Server (Production)

**Best for production use**

```bash
python api_server.py
```

**Access:**

- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

**API Endpoints:**

| Method | Endpoint                    | Purpose                  |
| ------ | --------------------------- | ------------------------ |
| GET    | `/`                         | API information          |
| GET    | `/health`                   | Health check             |
| POST   | `/query`                    | Submit query             |
| GET    | `/history/{session_id}`     | Get conversation history |
| GET    | `/pending-code`             | List pending code        |
| POST   | `/approve-code`             | Approve/reject code      |
| GET    | `/approved-code/{filename}` | Download approved code   |
| GET    | `/knowledge/search`         | Search knowledge base    |
| GET    | `/agents/list`              | List agents              |

---

## 💡 EXAMPLE QUERIES & WORKFLOWS

### Example 1: Build an AI Agent

**Query:** "Build me a customer support AI agent that can handle FAQs and create support tickets"

**Workflow:**

1. HR Manager analyzes → Routes to AI Engineer
2. AI Engineer generates Python code
3. Code saved to `./agent_workspace/pending_approval/`
4. User reviews and approves
5. Approved code moves to `./agent_workspace/approved/`

### Example 2: Data Analysis

**Query:** "Analyze our sales data from the database and create a revenue report"

**Workflow:**

1. HR Manager → Data Analyst
2. Data Analyst queries database
3. Generates analysis and visualizations
4. Creates Excel report
5. Saves to workspace

### Example 3: Security Audit

**Query:** "Run a security scan on our web application"

**Workflow:**

1. HR Manager → Security Agent
2. Security Agent runs multiple scans:
   - Nmap port scanning
   - Nuclei vulnerability scanning
   - SQLMap injection testing
   - ZAP web app scanning
3. Generates comprehensive report
4. Saves to workspace

### Example 4: Project Management

**Query:** "Schedule interviews for 3 new AI engineers and update the project timeline"

**Workflow:**

1. HR Manager → PMO Agent
2. PMO creates Jira tickets
3. Sends email notifications
4. Updates project database
5. Generates status report

---

## 🔧 CONFIGURATION DETAILS

### Model Configuration

**Recommended Models (Free):**

| Model                              | Quality   | Speed  | Best For        |
| ---------------------------------- | --------- | ------ | --------------- |
| mistralai/Mistral-7B-Instruct-v0.2 | Excellent | Medium | General use     |
| HuggingFaceH4/zephyr-7b-beta       | Very Good | Medium | Technical tasks |
| microsoft/Phi-3-mini-4k-instruct   | Good      | Fast   | Quick responses |

### Agent-Specific Settings

Each agent has optimized temperature settings:

| Agent        | Temperature | Reason                          |
| ------------ | ----------- | ------------------------------- |
| HR Manager   | 0.3         | Needs consistency in routing    |
| AI Engineer  | 0.5         | Balance creativity and accuracy |
| Data Analyst | 0.4         | Precision for data work         |
| PMO          | 0.3         | Consistency in management       |
| Security     | 0.2         | High precision required         |
| DevOps       | 0.2         | Exact commands needed           |

---

## 🧠 MEMORY SYSTEM

### How Memory Works

The system uses **ChromaDB** (vector database) to store and retrieve information:

- **Conversation History**: Remembers user interactions
- **Knowledge Base**: Stores agent-generated insights
- **Project Context**: Maintains ongoing project information
- **Agent Outputs**: Saves results for future reference

### Memory Operations

| Operation         | Purpose                   | Storage Location              |
| ----------------- | ------------------------- | ----------------------------- |
| Save Conversation | Remember user queries     | `./data/memory/[session_id]/` |
| Search Knowledge  | Find relevant information | Vector similarity search      |
| Save Insights     | Store agent learnings     | Knowledge base collection     |
| Context Retrieval | Provide relevant history  | Session-based                 |

---

## 🔒 SECURITY FEATURES

### Code Approval Workflow

```
1. AI Engineer generates code
   ↓
2. Code saved to ./agent_workspace/pending_approval/
   ↓
3. User reviews code (via API or local test)
   ↓
4a. APPROVED → moves to ./agent_workspace/approved/
4b. REJECTED → deleted
```

### Security Measures

- **No Direct Code Execution**: All generated code requires approval
- **Isolated Environment**: Agents run in controlled environment
- **API Key Protection**: Keys stored securely in .env
- **Input Validation**: All inputs validated before processing
- **Audit Logging**: All actions logged for review

---

## 🚨 TROUBLESHOOTING GUIDE

### Common Issues & Solutions

#### Issue: "HUGGINGFACE_API_KEY not found"

**Solution:**

```bash
# Check .env file
type .env

# Should contain:
HUGGINGFACE_API_KEY=hf_your_actual_token_here
```

#### Issue: "Model loading takes forever"

**Solution:**

```bash
# Use faster model in .env
HF_MODEL_NAME=microsoft/Phi-3-mini-4k-instruct
```

#### Issue: "Import errors"

**Solution:**

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Or install specific packages
pip install crewai crewai-tools langchain chromadb
```

#### Issue: "Database connection failed"

**Solution:**

- Check if `company.db` exists
- Ensure write permissions on directory
- Verify SQLite3 installation

#### Issue: "API server won't start"

**Solution:**

```bash
# Check if port 8000 is free
netstat -an | find "8000"

# Use different port
set API_PORT=8001
python api_server.py
```

#### Issue: "Memory system not working"

**Solution:**

- Check `./data/memory/` directory exists
- Ensure write permissions
- Verify ChromaDB installation

---

## 📊 PERFORMANCE OPTIMIZATION

### Speed Improvements

1. **Use Faster Models:**

   ```bash
   HF_MODEL_NAME=microsoft/Phi-3-mini-4k-instruct
   ```

2. **Reduce Token Limits:**
   - Edit `src/llm_config.py`
   - Lower `max_tokens` from 512 to 256

3. **Optimize Agent Prompts:**
   - Be specific in queries
   - Provide context upfront

### Quality Improvements

1. **Use Better Models:**

   ```bash
   HF_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2
   ```

2. **Provide Detailed Instructions:**
   - Include specific requirements
   - Mention preferred technologies

3. **Use Follow-up Queries:**
   - Refine results iteratively
   - Build upon previous work

---

## 🔗 INTEGRATION EXAMPLES

### N8N Workflow Integration

The system generates N8N workflow files for automation:

```yaml
# Example: customer_support_agent.n8n.yaml
nodes:
  - name: Webhook
    type: n8n-nodes-base.webhook
  - name: AI Agent
    type: custom.ai-company-agent
  - name: Response
    type: n8n-nodes-base.respondToWebhook
```

### Google ADK Deployment

Generated agents include Google ADK configuration for cloud deployment:

```python
# Example: customer_support_agent_adk.py
from google.adk.agents import BaseAgent

class CustomerSupportAgentADK(BaseAgent):
    def __init__(self):
        super().__init__(name="customer_support_agent")

    def process_request(self, user_input: str) -> str:
        # Agent logic here
        return "Response"
```

---

## 📈 MONITORING & LOGGING

### Log Levels

| Level    | Purpose             | When to Use      |
| -------- | ------------------- | ---------------- |
| DEBUG    | Detailed debugging  | Development      |
| INFO     | General information | Normal operation |
| WARNING  | Warning messages    | Potential issues |
| ERROR    | Error conditions    | Failures         |
| CRITICAL | Critical errors     | System failures  |

### Monitoring Endpoints

- **Health Check:** `GET /health`
- **System Stats:** `GET /stats`
- **Agent List:** `GET /agents/list`
- **Memory Status:** Check ChromaDB directory

---

## 🎯 BEST PRACTICES

### Query Writing

**Good Query:**

```
"Build a Python Flask API for user authentication with JWT tokens, including password hashing and email verification"
```

**Bad Query:**

```
"Build an API"
```

### Code Review Process

1. **Always Review Generated Code**
2. **Test in Isolated Environment**
3. **Check for Security Issues**
4. **Verify Dependencies**
5. **Test Functionality**

### Resource Management

- **Monitor API Usage:** Hugging Face has rate limits
- **Clean Old Data:** Periodically clean memory directory
- **Backup Important Code:** Keep approved agents safe
- **Update Dependencies:** Regularly update Python packages

---

## 🚀 ADVANCED FEATURES

### Multi-Agent Collaboration

Agents can work together on complex tasks:

```
User Query: "Build a full e-commerce platform"
↓
HR Manager breaks down into tasks:
├── AI Engineer: Build product catalog API
├── Data Analyst: Design database schema
├── Security: Implement authentication
├── DevOps: Set up deployment pipeline
└── PMO: Track project progress
```

### Custom Agent Creation

The system can generate new agent types based on user requirements.

### External API Integration

Through MCP servers, agents can integrate with:

- **Jira** for project management
- **GitHub** for code repositories
- **Email** for notifications
- **Web Search** for information gathering

---

## 📚 GLOSSARY

| Term             | Meaning                                       |
| ---------------- | --------------------------------------------- |
| **Agent**        | AI worker specialized in specific tasks       |
| **MCP**          | Model Context Protocol - external tool access |
| **CrewAI**       | Framework for multi-agent collaboration       |
| **ChromaDB**     | Vector database for memory storage            |
| **Hugging Face** | AI model hosting platform                     |
| **FastAPI**      | Modern Python web framework                   |
| **SQLite**       | Lightweight database engine                   |
| **ADK**          | Agent Development Kit (Google)                |

---

## 🆘 SUPPORT & COMMUNITY

### Getting Help

1. **Check Logs:** Look in console output for error messages
2. **Review Configuration:** Verify .env settings
3. **Test Components:** Use `test_local.py` for isolated testing
4. **Check Documentation:** This guide covers most issues

### Common Questions

**Q: Do I need OpenAI/Azure?**
A: No! This uses free Hugging Face models.

**Q: How much does it cost?**
A: Free! Hugging Face free tier works great.

**Q: Can I use my own AI model?**
A: Yes! Modify `src/llm_config.py`

**Q: Does it work offline?**
A: No, needs internet for Hugging Face API.

**Q: How do I approve generated code?**
A: Use `test_local.py` or API endpoint `/approve-code`

---

## 🎉 CONCLUSION

The AI Company represents a complete multi-agent AI system that demonstrates the power of collaborative AI agents. With proper setup and understanding, it can handle complex real-world tasks across multiple domains.

**Key Takeaways:**

- 🤖 **6 Specialized Agents** working together
- 🔧 **Real Tool Integration** through MCP servers
- 💾 **Persistent Memory** and database storage
- 🚀 **Production Ready** with FastAPI
- 💯 **100% Free** infrastructure

**Next Steps:**

1. Follow installation guide
2. Get Hugging Face API key
3. Run `python test_local.py`
4. Try building your first AI agent!

---

_This documentation covers the complete AI Company system. For technical details, see individual source files. Last updated: 2024_
