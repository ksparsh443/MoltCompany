# AI Company - Agent Documentation

> A Multi-Agent AI System built on Google ADK with 7 Specialist Agents

**Version:** 2.0.0
**Last Updated:** 2026-02-07
**LLM Providers:** HuggingFace (FREE), Ollama (FREE), Gemini, OpenAI
**Database:** Supabase (PostgreSQL) / SQLite (fallback)

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Agent Hierarchy](#agent-hierarchy)
3. [HR Manager](#1-hr-manager-root-orchestrator)
4. [AI Engineer](#2-ai-engineer)
5. [Data Analyst](#3-data-analyst)
6. [PMO/Scrum Master](#4-pmoscrum-master)
7. [Security Pentester](#5-security-pentester)
8. [DevOps Engineer](#6-devops-engineer)
9. [Sales & Marketing](#7-sales--marketing)
10. [Database Schema](#database-schema)
11. [Configuration](#configuration)
12. [Quick Start](#quick-start)

---

## Architecture Overview

```
                    +-------------------+
                    |   HR_Manager      |
                    | (Root Orchestrator)|
                    +--------+----------+
                             |
        +--------------------+--------------------+
        |          |          |          |        |         |
   +----v----+ +---v----+ +---v---+ +----v---+ +--v---+ +---v----+
   |   AI    | | Data   | |  PMO  | |Security| |DevOps| | Sales  |
   |Engineer | |Analyst | |Scrum  | |Pentest | |Eng   | |Market  |
   +---------+ +--------+ +-------+ +--------+ +------+ +--------+
```

### Key Features

- **Multi-Agent Orchestration**: HR Manager routes tasks to specialists
- **FREE LLM Options**: HuggingFace Mistral-7B, Ollama llama3.1
- **Cloud Database**: Supabase PostgreSQL with SQLite fallback
- **End-to-End CI/CD**: Full pipeline with security scanning
- **Predictive HR Analytics**: Burnout detection, hidden talent discovery

---

## Agent Hierarchy

| Agent | Role | Temperature | Tools |
|-------|------|-------------|-------|
| HR_Manager | Orchestrator & HR Operations | 0.3 | 21 |
| AI_Engineer | Full-Stack Code Generation | 0.5 | 20 |
| Data_Analyst | RAG, Dashboards, Visualization | 0.4 | 24 |
| PMO_Scrum_Master | Project Management | 0.3 | 6 |
| Security_Pentester | Security Testing & Pentest | 0.2 | 19 |
| DevOps_Engineer | Infrastructure & CI/CD | 0.2 | 5 |
| Sales_Marketing | Content & Customer Retention | 0.7 | 13 |

---

## 1. HR Manager (Root Orchestrator)

### Overview
The HR Manager is the root agent that orchestrates all other agents and provides a comprehensive self-service HR operations platform.

### Capabilities

#### Recruitment & Talent Acquisition
- **LinkedIn Profile Search** (FREE via DuckDuckGo)
  ```python
  search_linkedin_profiles(
      job_title="Senior Python Developer",
      skills="Python, FastAPI, PostgreSQL",
      location="San Francisco",
      num_results=10
  )
  ```

- **Resume Parsing** (PDF, DOCX, TXT)
  ```python
  parse_resume("john_doe_resume.pdf")
  # Returns: email, phone, skills, experience_years, linkedin_url
  ```

- **Candidate Matching**
  ```python
  match_candidates_to_jd("jd_senior_python_developer_20260207")
  # Returns ranked candidates with match scores
  ```

#### Interview Scheduling
```python
schedule_interview(
    candidate_id="cand_20260207123456",
    interviewer_email="hiring.manager@company.com",
    interview_type="technical",  # technical, behavioral, culture, final
    duration_minutes=60
)
# Auto-sends calendar invites and email notifications
```

#### Invisible Onboarding (Zero Manual Work)
```python
# 1. Generate contract
generate_contract(
    employee_name="John Doe",
    role="Senior Python Developer",
    department="Engineering",
    salary=150000,
    start_date="2026-03-01",
    manager="Jane Smith"
)

# 2. Initiate onboarding
initiate_onboarding(
    employee_name="John Doe",
    email="john.doe@company.com",
    role="Senior Python Developer",
    department="Engineering",
    manager="Jane Smith",
    start_date="2026-03-01"
)
# Triggers: Welcome emails, system provisioning, equipment, training schedule
```

#### Performance Monitoring & Talent Intelligence

**Predictive Burnout Alerts:**
```python
predict_burnout_risk(department="Engineering", threshold=0.6)
# Returns: At-risk employees with predictions like
# "This workload pattern has led to burnout in similar teams within 6 weeks"
```

**Hidden Talent Detection:**
```python
detect_hidden_talent(min_growth_potential=0.7)
# Surfaces high-impact contributors overlooked by traditional reviews
```

**Auto-Generated Performance Reviews:**
```python
generate_performance_review("emp_123")
# Creates review from real delivery signals, quality metrics, collaboration data
```

#### Predictive Compliance Alerts
```python
check_compliance_alerts()
# Alerts: "Based on hiring plans, you'll need additional visa slots - start applications now"
```

### Tools (21 total)
| Tool | Description |
|------|-------------|
| `search_linkedin_profiles` | Search LinkedIn via DuckDuckGo (FREE) |
| `parse_resume` | Extract data from PDF/DOCX/TXT resumes |
| `match_candidates_to_jd` | AI-powered candidate ranking |
| `schedule_interview` | Auto-schedule with calendar/email |
| `send_interview_invite` | Send interview invitations |
| `create_job_description` | Create and save JDs |
| `generate_contract` | Auto-generate employment contracts |
| `initiate_onboarding` | Zero-manual-work onboarding |
| `update_onboarding_status` | Track onboarding progress |
| `analyze_employee_performance` | Performance metrics analysis |
| `detect_hidden_talent` | Find overlooked high performers |
| `predict_burnout_risk` | Predictive burnout alerts |
| `generate_performance_review` | Auto-generate reviews |
| `check_compliance_alerts` | Predictive compliance alerts |
| `get_hr_dashboard` | Comprehensive HR metrics |
| `search_memory` | Knowledge base search |
| `save_to_memory` | Store knowledge |
| `send_email` | Email communication |
| `web_search` | Web research |
| `execute_sql` | Database queries |

---

## 2. AI Engineer

### Overview
A Vercel/Bolt/dev.atoms-style code generation agent with full CI/CD pipeline.

### 6-Phase Workflow

```
Phase 1: Requirements Analysis
    ↓
Phase 2: Architecture Design
    ↓
Phase 3: Code Generation (3 Tech Stacks)
    ↓
Phase 4: Security Scanning
    ↓
Phase 5: Unit Testing
    ↓
Phase 6: GitHub Deployment
```

### Capabilities

#### Multi-Stack Code Generation
Generates complete projects in:
- **Python/FastAPI** - Best for AI/ML, data processing
- **Node.js/Express** - Best for real-time, JavaScript ecosystem
- **Go/Gin** - Best for high-performance, concurrent systems

Each stack includes:
- Main application code
- README.md (comprehensive documentation)
- DEPLOYMENT.md (Vercel, Railway, Render, Docker options)
- SETUP_GUIDE.md (layman-friendly setup instructions)
- Unit tests
- Dockerfile
- .env.example
- .gitignore

#### Security Scanning (FREE Tools)
- **Bandit** - Python security scanner
- **Safety** - Python dependency vulnerabilities
- **npm audit** - Node.js vulnerabilities
- **gosec** - Go security scanner

#### CI/CD Pipeline
```python
# Create and run full pipeline
result = run_full_pipeline(
    project_id="inventory_api_20260207",
    tech_stack="python",
    github_repo="https://github.com/user/repo",
    target_url="https://app.example.com"
)
# Runs: Source checks, Security scan, Unit tests, Deployment checks, GitHub checks, Pentest
```

### Tools (20 total)
| Tool | Description |
|------|-------------|
| `analyze_requirements` | Parse task, extract requirements |
| `generate_architecture` | Create system design docs |
| `generate_full_project` | Complete code in one stack |
| `generate_all_stacks` | Generate Python + Node.js + Go |
| `create_pipeline` | Initialize CI/CD pipeline |
| `run_full_pipeline` | Execute all 6 stages |
| `get_pipeline_status` | Check test results |
| `list_pipelines` | View all pipelines |
| `run_security_scan_full` | Complete security scan |
| `run_security_scan` | General security scan |
| `run_unit_tests` | Execute tests |
| `update_test_status` | Manual status update |
| `push_to_github` | Deploy to GitHub |
| `save_code_file` | Save code files |
| `read_file` | Read files |
| `write_file` | Write files |
| `list_files` | List directory |
| `search_memory` | Knowledge search |
| `save_to_memory` | Store knowledge |
| `web_search` | Web research |

---

## 3. Data Analyst

### Overview
Expert Data Analyst with **RAG capabilities**, **interactive Plotly visualizations**, and **Power BI-like dashboard generation**. All tools are FREE - no paid APIs required.

### Data Analysis Workflow
```
Phase 1: Ingest Data (CSV, XLSX, PDF, TXT)
    ↓
Phase 2: Query Data (SQL or RAG natural language)
    ↓
Phase 3: Create Visualizations (Interactive Plotly charts)
    ↓
Phase 4: Build Dashboards (Power BI alternative)
    ↓
Phase 5: Analyze Resources & Generate Reports
```

### Capabilities

#### Data Ingestion (RAG-enabled)
```python
# Ingest from local files
ingest_data_file(
    file_path="sales_data.csv",
    source_name="Q4 Sales Data"
)
# Returns: source_id for querying

# Ingest from cloud (FREE - no API keys)
fetch_from_google_drive("https://drive.google.com/file/d/xxx/view")
fetch_from_sharepoint("https://company.sharepoint.com/shared/report.xlsx")
```

**Supported Formats:**
- CSV - Tabular data with SQL querying
- XLSX/XLS - Excel spreadsheets
- PDF - Text extraction + table parsing + RAG indexing
- TXT - Full text with RAG search

#### Data Querying
```python
# SQL Query on tabular data
query_data(
    source_id="DS-20260207123456",
    query="SELECT region, SUM(revenue) FROM data GROUP BY region",
    query_type="sql"
)

# RAG Query on text data (PDF, TXT)
query_data(
    source_id="DS-20260207789012",
    query="What are the key findings from Q4?",
    query_type="rag"
)

# Aggregation
query_data(source_id="DS-xxx", query="*", query_type="aggregate")
# Returns: Statistical summary (mean, std, min, max, etc.)
```

#### Interactive Visualizations (Plotly)
```python
create_interactive_chart(
    source_id="DS-20260207123456",
    chart_type="bar",        # bar, line, scatter, pie, heatmap, histogram, box, area, funnel, treemap
    x_column="month",
    y_column="revenue",
    title="Monthly Revenue 2025",
    color_column="region",   # Optional: group by color
    aggregation="sum"        # none, sum, mean, count, min, max
)
# Returns: Interactive HTML + PNG image
```

#### Power BI-like Dashboards (FREE)
```python
create_dashboard(
    title="Executive Sales Dashboard",
    description="Q4 2025 Performance Overview",
    source_ids="DS-001,DS-002",
    charts_config='''[
        {"type": "bar", "x": "month", "y": "revenue", "title": "Monthly Revenue"},
        {"type": "pie", "x": "region", "y": "sales", "title": "Sales by Region"},
        {"type": "line", "x": "date", "y": "users", "color": "channel", "title": "User Growth"},
        {"type": "heatmap", "x": "day", "y": "hour", "color": "activity", "title": "Activity Heatmap"}
    ]'''
)
```

**Dashboard Features:**
- Modern dark theme UI
- KPI cards with automatic totals
- Multiple chart layouts (2-column grid)
- Interactive Plotly charts
- Data table preview
- Standalone HTML (works offline)
- No server required

#### Resource Management Analysis
```python
analyze_resource_utilization(
    source_id="DS-team-allocation",
    time_column="date",
    resource_column="employee_name",
    value_column="hours_worked"
)
# Returns:
# - Utilization metrics by resource
# - Overutilization alerts (>90%)
# - Underutilization alerts (<30%)
# - Time-based trends
# - Recommendations for rebalancing
```

#### Reports & Logging
```python
# Export comprehensive report
export_analysis_report(
    source_id="DS-xxx",
    report_type="full",    # full, summary, statistical
    format="html"          # html, markdown
)

# View data catalog
get_data_catalog()
# Returns: All ingested sources with stats

# View dashboards
get_dashboards()

# Audit logs
get_data_operation_logs(days=7)
```

#### Database Operations (Supabase + SQLite)
```python
# Raw SQL
execute_sql("SELECT * FROM employees WHERE department='Engineering'")

# Supabase client API
supabase_select("employees", "*", '{"department": "Engineering"}')
supabase_insert("employees", '{"name": "John", "role": "Developer"}')
```

### Database Tables
- `data_catalog` - Tracks all ingested data sources
- `data_query_logs` - Query audit trail
- `visualization_logs` - Chart creation logs
- `dashboards` - Dashboard registry

### Tools (24 total)
| Tool | Description |
|------|-------------|
| `ingest_data_file` | Ingest CSV, XLSX, PDF, TXT files |
| `query_data` | SQL or RAG queries on data |
| `get_data_catalog` | List all data sources |
| `fetch_from_google_drive` | Download from Google Drive (FREE) |
| `fetch_from_sharepoint` | Download from SharePoint/OneDrive |
| `create_interactive_chart` | Plotly charts (10+ types) |
| `create_dashboard` | Power BI-like dashboards |
| `get_dashboards` | List all dashboards |
| `analyze_resource_utilization` | Resource management analysis |
| `export_analysis_report` | Generate HTML/Markdown reports |
| `get_data_operation_logs` | Audit trail of operations |
| `execute_sql` | Run SQL queries |
| `get_database_schema` | View table structures |
| `get_database_info` | Check connection status |
| `supabase_select` | Supabase client select |
| `supabase_insert` | Supabase client insert |
| `supabase_update` | Supabase client update |
| `supabase_delete` | Supabase client delete |
| `create_visualization` | Basic charts |
| `search_memory` | Knowledge search |
| `save_to_memory` | Store knowledge |
| `write_file` | Write files |
| `read_file` | Read files |

### FREE Tools Used
- **Plotly** - Interactive charts (pip install plotly)
- **Dash** - Dashboard framework (pip install dash)
- **pandas** - Data processing (pip install pandas)
- **pdfplumber** - PDF extraction (pip install pdfplumber)
- **openpyxl** - Excel support (pip install openpyxl)
- **gdown** - Google Drive download (pip install gdown)
- **ChromaDB** - RAG vector store (pip install chromadb)

---

## 4. PMO/Scrum Master

### Overview
Comprehensive project management with task tracking, Excel reporting, meeting management, and MOM (Minutes of Meeting) automation.

### Capabilities

#### Task Management
```python
# Create task
create_task(
    title="Implement login API",
    description="Build OAuth2 login endpoint",
    project="MyProject",
    assignee="john@company.com",
    priority="high",  # low, medium, high, critical
    due_date="2026-02-15",
    sprint="SPR-001",
    story_points=5
)

# Update task
update_task("TASK-123", status="in_progress", blockers="Waiting for design")

# Get tasks with filters
get_tasks(project="MyProject", status="in_progress", assignee="john")

# Get summary
get_task_summary("MyProject", "SPR-001")
```

#### Sprint Management
```python
# Create sprint
create_sprint(
    name="Sprint 24",
    project="MyProject",
    goal="Complete user authentication",
    start_date="2026-02-10",
    end_date="2026-02-24",
    committed_points=40
)

# Get sprint status with burndown data
get_sprint_status("SPR-001")
# Returns: velocity, completion %, remaining points, blockers
```

#### Excel Trackers (FREE - openpyxl)
```python
# Create Excel spreadsheet
create_excel_tracker(
    tracker_name="Sprint24_Status",
    tracker_type="sprint",  # sprint, project, tasks, burndown
    project="MyProject",
    sprint="SPR-001"
)
# Creates color-coded Excel with task status, summary sheet

# Update tracker
update_excel_tracker(
    "Sprint24_Status.xlsx",
    '[{"task_id":"TASK-123","field":"status","value":"done"}]'
)
```

#### Meeting Scheduling
```python
# Schedule meeting with Google Calendar
schedule_meeting(
    title="Sprint Review",
    meeting_type="sprint_review",  # daily_standup, sprint_planning, retrospective, adhoc
    scheduled_at="2026-02-24T14:00",
    duration_minutes=60,
    attendees="team@company.com,stakeholder@company.com",
    agenda="1. Demo features\n2. Discuss blockers\n3. Plan next sprint"
)
# Sends calendar invites and Google Meet link
```

#### Minutes of Meeting (MOM)
```python
# Create comprehensive meeting minutes
create_meeting_minutes(
    meeting_id="MTG-20260224...",
    attendees="John, Jane, Bob",
    absentees="Alice (sick)",
    discussion_points="Discussed API design, Reviewed security concerns",
    decisions="Approved OAuth2 implementation, Deferred caching to Sprint 25",
    action_items='[
        {"description":"Fix login bug","assignee":"John","due_date":"2026-02-26"},
        {"description":"Update docs","assignee":"Jane","due_date":"2026-02-28"}
    ]',
    next_meeting="2026-03-01T14:00",
    notes="Good progress overall"
)
# Creates MOM document and sends to all attendees
```

#### Action Item Tracking
```python
# Get open action items
get_action_items(status="open")
# Shows overdue items

# Update action item
update_action_item("ACT-MTG-001-1", status="done")
```

#### Daily Standups
```python
# Record standup update
record_standup(
    team="Engineering",
    participant="John Doe",
    yesterday="Completed API endpoint",
    today="Working on unit tests",
    blockers="Need design review"
)

# Generate standup report
get_standup_report("Engineering", "2026-02-07")

# Send reminders
send_standup_reminder("Engineering", "09:00")
```

#### PMO Dashboard
```python
get_pmo_dashboard("MyProject")
# Returns:
# - Task completion rates
# - Active sprint status
# - Upcoming meetings
# - Open/overdue action items
# - Standup participation
# - Blockers
```

### Tools (26 total)
| Tool | Description |
|------|-------------|
| `create_task` | Create tasks with full details |
| `update_task` | Update task status/assignee/blockers |
| `get_tasks` | Filter and list tasks |
| `get_task_summary` | Task statistics |
| `create_sprint` | Create new sprints |
| `get_sprint_status` | Sprint metrics & burndown |
| `create_excel_tracker` | Generate Excel spreadsheets |
| `update_excel_tracker` | Update existing trackers |
| `schedule_meeting` | Schedule with Google Calendar |
| `create_meeting_minutes` | Create MOM documents |
| `get_action_items` | Get meeting action items |
| `update_action_item` | Update action item status |
| `record_standup` | Record standup updates |
| `get_standup_report` | Generate standup reports |
| `send_standup_reminder` | Send reminders |
| `get_pmo_dashboard` | Comprehensive metrics |
| `create_jira_ticket` | Create Jira tickets |
| `update_jira_ticket` | Update Jira tickets |
| `send_email` | Send notifications |
| `search_memory` | Knowledge search |
| `save_to_memory` | Store knowledge |
| `execute_sql` | Database queries |
| `write_file` | Write files |
| `read_file` | Read files |

### Output Files
```
agent_workspace/pmo/
├── trackers/     # Excel spreadsheets
├── meetings/     # MOM documents (markdown)
├── reports/      # Status reports
└── sprints/      # Sprint data
```

---

## 5. Security Pentester

### Overview
Comprehensive security testing with OWASP Top 10 coverage and **real-time penetration testing** with test case tracking on deployed application URLs.

### Security Workflow
```
Phase 1: Create Pentest Session (track target)
    ↓
Phase 2: Execute Security Scans (network, web, injection)
    ↓
Phase 3: Review & Track Test Cases (pass/fail)
    ↓
Phase 4: Generate Report with Vulnerabilities
```

### Capabilities

#### Real-Time Penetration Testing (NEW)

**Step 1: Create Pentest Session**
```python
create_pentest_session(
    target_url="https://myapp.example.com",
    target_type="web_application",  # web_application, api, network
    scope="Full security assessment of production app"
)
# Returns: session_id for tracking all tests
```

**Step 2: Run Security Scans**
```python
run_pentest_scan(
    session_id="sess_20260207_abc123",
    scan_type="comprehensive",  # quick, standard, comprehensive
    test_categories=["network", "web", "injection", "discovery"]
)
# Runs 12+ security tests:
# - Port scanning & service enumeration
# - HTTP methods & SSL/TLS analysis
# - Security headers & cookie checks
# - SQL injection, XSS, command injection
# - Sensitive files, directory listing, error handling
# - CORS misconfiguration
```

**Step 3: Review & Update Test Results**
```python
# Get all test results
get_pentest_results(session_id="sess_20260207_abc123")
# Returns: test cases with status, vulnerabilities found

# Update individual test status
update_pentest_test(
    test_id="test_20260207_xyz789",
    status="fail",  # pass, fail, pending, skipped
    notes="SQL injection confirmed on /api/users endpoint"
)
```

**Step 4: Generate Report**
```python
generate_pentest_report(
    session_id="sess_20260207_abc123",
    report_format="markdown"  # markdown, json
)
# Report includes:
# - Executive summary with risk score
# - Test pass/fail statistics
# - All vulnerabilities with OWASP/CWE references
# - Remediation recommendations
```

**Step 5: List & Manage Sessions**
```python
list_pentest_sessions(
    target_url="https://myapp.example.com",  # optional filter
    status="in_progress"  # in_progress, completed, cancelled
)
```

#### Test Categories Covered

| Category | Tests Performed |
|----------|-----------------|
| **Network** | Port scan (common ports), service enumeration |
| **Web** | HTTP methods, SSL/TLS, headers, cookies |
| **Injection** | SQL injection, XSS (reflected, stored, DOM), command injection |
| **Discovery** | Sensitive files (backup, config), directory listing, error handling |
| **CORS** | Cross-origin misconfigurations |

#### Vulnerability Severity Levels

| Level | CVSS Score | Action |
|-------|------------|--------|
| CRITICAL | 9.0-10.0 | Immediate remediation |
| HIGH | 7.0-8.9 | Fix before production |
| MEDIUM | 4.0-6.9 | Fix in next release |
| LOW | 0.1-3.9 | Consider for future |
| INFO | 0.0 | Informational only |

#### Code Security (Static Analysis)
```python
run_security_scan("/path/to/code", "full")
# Uses: Bandit, Safety, Semgrep
```

#### OWASP Top 10 (2021)
```python
run_owasp_scan("https://example.com", "all")
# Covers:
# A01: Broken Access Control
# A02: Cryptographic Failures
# A03: Injection (SQL, XSS, Command)
# A04: Insecure Design
# A05: Security Misconfiguration
# A06: Vulnerable Components
# A07: Authentication Failures
# A08: Integrity Failures
# A09: Logging Failures
# A10: SSRF
```

### FREE Tools Used
- **Python socket/ssl** - Network and SSL testing (built-in)
- **Python urllib** - HTTP security testing (built-in)
- **Bandit** - Python security (pip install bandit)
- **Safety** - Python dependencies (pip install safety)
- **Semgrep** - Multi-language SAST (pip install semgrep)
- **npm audit** - Node.js vulnerabilities (built-in)

### Database Tables
- `pentest_sessions` - Track pentest sessions with status
- `pentest_test_cases` - Individual test results (pass/fail)
- `pentest_vulnerabilities` - Discovered vulnerabilities with OWASP/CWE

### Tools (19 total)
| Tool | Description |
|------|-------------|
| `create_pentest_session` | Create new pentest session for target |
| `run_pentest_scan` | Execute security scans (network, web, injection) |
| `get_pentest_results` | Get test results and vulnerabilities |
| `update_pentest_test` | Update test status (pass/fail) |
| `generate_pentest_report` | Generate markdown/JSON report |
| `list_pentest_sessions` | List all pentest sessions |
| `run_security_scan` | Bandit, Safety, Semgrep |
| `run_web_security_scan` | Headers, SSL, cookies |
| `run_owasp_scan` | OWASP Top 10 assessment |
| `run_code_security_review` | Language-specific SAST |
| `scan_dependencies` | Vulnerable packages |
| `generate_security_report` | Static analysis reports |
| `run_security_scan_full` | Complete project scan |
| `write_file` | Write files |
| `read_file` | Read files |
| `list_files` | List directory |
| `search_memory` | Knowledge search |
| `save_to_memory` | Store knowledge |
| `execute_sql` | Database queries |

---

## 6. DevOps Engineer

### Overview
Infrastructure deployment and CI/CD pipeline management.

### Capabilities
- Deploy infrastructure
- Security scanning
- Configuration management
- Monitoring setup

### Tools (5 total)
| Tool | Description |
|------|-------------|
| `deploy_infrastructure` | Provision resources |
| `run_security_scan` | Security checks |
| `write_file` | Config files |
| `search_memory` | Knowledge search |
| `save_to_memory` | Store knowledge |

---

## 7. Sales & Marketing

### Overview
Content creation, customer retention, and social media strategy using FREE APIs.

### Capabilities

#### Trending Topic Research (FREE)
```python
# DuckDuckGo Search
search_trending_topics("AI trends 2026", num_results=10)

# HackerNews
fetch_hackernews_trends(num_stories=10, keyword_filter="AI")
```

#### Content Creation
```python
# Video Scripts
generate_video_script(
    topic="AI in Healthcare",
    duration_seconds=30,
    platform="linkedin"
)

# Social Captions
generate_social_caption(
    topic="AI trends",
    platform="twitter",
    include_hashtags=True
)

# Content Calendar
generate_content_calendar(
    topics="AI, Machine Learning, Data Science",
    platforms="linkedin,twitter",
    posts_per_week=5
)
```

#### Churn Analysis
```python
analyze_churn_risk(time_period="30d")
# Returns risk indicators and recommendations
```

#### UX Friction Detection
```python
detect_ux_friction(
    url="https://example.com/signup",
    flow_type="signup",
    device_type="mobile"
)
# Returns friction categories and checklist
```

### Tools (13 total) - ALL FREE
| Tool | Description |
|------|-------------|
| `search_trending_topics` | DuckDuckGo search (FREE) |
| `fetch_hackernews_trends` | HackerNews API (FREE) |
| `generate_video_script` | Script templates |
| `generate_social_caption` | Caption templates |
| `analyze_churn_risk` | Risk framework |
| `detect_ux_friction` | UX analysis |
| `generate_content_calendar` | Calendar planning |
| `get_analyst_insights` | Memory search |
| `search_memory` | Knowledge search |
| `save_to_memory` | Store knowledge |
| `web_search` | Web research |
| `write_file` | Write files |
| `execute_sql` | Database queries |

---

## Database Schema

### Core Tables
```sql
-- Employees
employees (id, name, role, email, department, hire_date)

-- Projects
projects (id, name, status, owner, start_date, end_date, budget)

-- Tickets
tickets (id, title, description, status, priority, assignee, created_at, updated_at)
```

### HR Tables
```sql
-- Candidates
candidates (candidate_id, name, email, linkedin_url, skills, experience_years, match_score, status)

-- Job Descriptions
job_descriptions (jd_id, title, department, required_skills, salary_min, salary_max, status)

-- Interviews
interviews (interview_id, candidate_id, interviewer, scheduled_at, meeting_link, status)

-- Onboarding
onboarding (onboarding_id, employee_id, checklist, systems_provisioned, status)

-- Performance Metrics
performance_metrics (metric_id, employee_id, burnout_risk, growth_potential, quality_score)

-- Compliance Alerts
compliance_alerts (alert_id, alert_type, severity, title, action_required, status)
```

### CI/CD Tables
```sql
-- Pipeline Runs
pipeline_runs (pipeline_id, project_id, status, passed_checks, failed_checks)

-- Test Cases
test_cases (test_id, pipeline_id, category, name, status, error_message)

-- Security Findings
security_findings (finding_id, pipeline_id, tool, severity, title, file_path)
```

---

## Configuration

### Environment Variables (.env)

```env
# LLM Provider (FREE options)
MODEL_PROVIDER=huggingface  # or: ollama, gemini, openai
HF_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2
HUGGINGFACE_API_KEY=hf_xxxxx

# Ollama (FREE, local)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL_NAME=llama3.1

# Supabase (Cloud PostgreSQL)
DB_PROVIDER=supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-key
SUPABASE_DB_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres

# Email (for HR notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Run the Agent System
```bash
python test_local.py
```

### 4. Example Queries

**Hiring:**
```
"Find Python developers in San Francisco with 5+ years experience"
"Schedule an interview with candidate cand_123 for tomorrow"
"Generate an employment contract for John Doe as Senior Developer at $150k"
```

**Code Generation:**
```
"Build an inventory management API with CRUD operations"
"Generate code in all three tech stacks with security scanning"
```

**Analytics:**
```
"Show me the sales report for Q1"
"Analyze employee performance for the Engineering team"
```

**Security:**
```
"Run a security scan on the new API"
"Check for OWASP Top 10 vulnerabilities on https://example.com"
```

**Marketing:**
```
"Find trending AI topics and create a LinkedIn post"
"Analyze churn risk for our customers"
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-02-07 | Added comprehensive HR Manager with LinkedIn search, onboarding, performance monitoring, burnout prediction |
| 1.5.0 | 2026-02-07 | Added Supabase integration, Sales & Marketing agent |
| 1.0.0 | 2026-02-07 | Initial release with 6 agents |

---

## License

MIT License - See LICENSE file for details.

---

*Generated by AI Company Agent System*
