# API Testing Guide - AI Company (Google ADK)

Base URL: `http://localhost:8000`
Swagger Docs: `http://localhost:8000/docs`

Start the server first:
```bash
cd D:\DerivHack
venv\Scripts\activate
python api_server.py
```

---

## 1. CORE SYSTEM (Test these first)

### 1.1 Root - API Info
```
GET http://localhost:8000/
```
Expected: JSON with API name, version, list of agents and endpoints.

### 1.2 Health Check
```
GET http://localhost:8000/health
```
Expected:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "agents_loaded": 7,
  "memory_status": "connected",
  "model_provider": "huggingface"
}
```
Verify `model_provider` shows `huggingface` (not `openai`).

### 1.3 Database Status
```
GET http://localhost:8000/db/status
```
Expected: `"status": "connected"`, `"provider": "supabase"`, `"test_query": "passed"`

### 1.4 Database Schema
```
GET http://localhost:8000/db/schema
```
Expected: List of tables (employees, projects, tickets, etc.)

### 1.5 List Agents
```
GET http://localhost:8000/agents/list
```
Expected: All 6 agents with their capabilities listed.

### 1.6 System Stats
```
GET http://localhost:8000/stats
```
Expected: System statistics JSON.

---

## 2. GITHUB & GOOGLE DRIVE (New integrations)

### 2.1 GitHub Status
```
GET http://localhost:8000/github/status
```
Expected:
```json
{
  "status": "connected",
  "username": "infovista04-alt",
  "token_set": true,
  "public_repos": 0
}
```

### 2.2 Google Drive Status
```
GET http://localhost:8000/drive/status
```
Expected:
```json
{
  "enabled": true,
  "connected": true,
  "root_folder_id": "1blt_IKlgqv_pZxK9nUWVrKb7OyaIqq3l",
  "service_account_exists": true
}
```

### 2.3 Drive Reload (after .env changes)
```
POST http://localhost:8000/drive/reload
```
Expected: Same as drive/status but freshly loaded from .env.

### 2.4 Drive Folder Structure
```
GET http://localhost:8000/drive/folders
```
Expected: List of agent folder mappings.

### 2.5 Drive Sync (uploads entire workspace)
```
POST http://localhost:8000/drive/sync
```
Expected: `"uploaded_count"` with number of files synced. Check your Google Drive folder after this!

---

## 3. QUERY ENGINE (Main AI endpoint)

### 3.1 Submit a Query
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"List all employees\", \"user_id\": \"test\"}"
```
Or in Swagger UI: POST /query with body:
```json
{
  "query": "List all employees",
  "user_id": "test",
  "stream": false
}
```
Expected: `"status": "success"` with agent response.

### 3.2 Get Conversation History
```
GET http://localhost:8000/history/session_12345?limit=10
```
Expected: History array (empty if no prior session).

---

## 4. HR MANAGER

### 4.1 Search Candidates
```bash
curl -X POST http://localhost:8000/hr/search-candidates \
  -H "Content-Type: application/json" \
  -d "{\"job_title\": \"AI Engineer\", \"skills\": \"Python, ML\", \"num_results\": 5}"
```
Expected: Search results from DuckDuckGo.

### 4.2 List Employees
```
GET http://localhost:8000/hr/employees?status=active
```
Expected: Employee list from database.

### 4.3 Onboard Employee
```bash
curl -X POST http://localhost:8000/hr/onboard \
  -H "Content-Type: application/json" \
  -d "{\"employee_name\": \"Test User\", \"email\": \"test@example.com\", \"role\": \"Engineer\", \"department\": \"Engineering\", \"manager_email\": \"manager@example.com\", \"start_date\": \"2026-03-01\"}"
```
Expected: Onboarding checklist created.

---

## 5. PMO / SCRUM MASTER

### 5.1 Create Task
```bash
curl -X POST http://localhost:8000/pmo/tasks \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Test Task\", \"description\": \"Testing API\", \"project\": \"TestProject\", \"priority\": \"high\"}"
```
Expected: Task created with ID.

### 5.2 List Tasks
```
GET http://localhost:8000/pmo/tasks?project=TestProject
```
Expected: Tasks array.

### 5.3 Schedule Meeting
```bash
curl -X POST http://localhost:8000/pmo/meetings \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Sprint Review\", \"meeting_type\": \"sprint_review\", \"scheduled_at\": \"2026-02-10T10:00:00\", \"duration_minutes\": 60, \"attendees\": \"team@company.com\"}"
```
Expected: Meeting created, ICS file generated.

### 5.4 Create Excel Tracker
```
POST http://localhost:8000/pmo/excel-tracker?tracker_name=sprint1&tracker_type=sprint
```
Expected: Excel file created in workspace.

---

## 6. SECURITY PENTESTER

### 6.1 Create Pentest Session
```bash
curl -X POST http://localhost:8000/security/pentest/session \
  -H "Content-Type: application/json" \
  -d "{\"target_url\": \"https://example.com\", \"target_type\": \"web_application\"}"
```
Expected: Session created with session_id.

### 6.2 Run Security Scan
```bash
curl -X POST http://localhost:8000/security/pentest/scan \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"SESSION_ID_FROM_ABOVE\", \"scan_type\": \"comprehensive\"}"
```
Expected: Scan results with findings.

### 6.3 List Security Sessions
```
GET http://localhost:8000/security/sessions
```
Expected: All pentest sessions.

---

## 7. DATA ANALYST

### 7.1 Data Catalog
```
GET http://localhost:8000/data/catalog
```
Expected: List of ingested data sources.

### 7.2 List Dashboards
```
GET http://localhost:8000/data/dashboards
```
Expected: Dashboard list (may be empty initially).

---

## 8. CODE MANAGEMENT

### 8.1 Pending Code
```
GET http://localhost:8000/pending-code
```
Expected: List of code files awaiting approval.

---

## 9. EMAIL & DESIGNATIONS

### 9.1 Email Config Status
```
GET http://localhost:8000/email/config-status
```
Expected: Shows if SMTP is configured (will say "simulated" if using placeholders).

### 9.2 Resolve Designation
```
GET http://localhost:8000/designations/resolve/HR_MANAGER
```
Expected: `"email": "sparshkandpal@gmail.com"`

---

## 10. TOKEN MONITORING

### 10.1 Token Consumption
```
GET http://localhost:8000/tokens/consumption
```
Expected: Token usage data (may be empty initially).

### 10.2 Token Summary
```
GET http://localhost:8000/tokens/summary
```
Expected: Real-time token totals per agent.

---

## 11. MEETING RECORDER

### 11.1 Meeting Recorder Page (Browser)
```
http://localhost:8000/meeting-recorder?meeting_id=TEST-001
```
Expected: Opens HTML page with Start/Stop recording buttons.

### 11.2 Active Recordings
```
GET http://localhost:8000/meetings/recording/active
```
Expected: List of active recording sessions.

---

## QUICK SMOKE TEST (Run these 8 to verify everything)

| # | Endpoint | Method | What to check |
|---|----------|--------|---------------|
| 1 | `/health` | GET | `model_provider: "huggingface"` |
| 2 | `/db/status` | GET | `status: "connected"` |
| 3 | `/github/status` | GET | `status: "connected"` |
| 4 | `/drive/status` | GET | `enabled: true, connected: true` |
| 5 | `/agents/list` | GET | 6 agents listed |
| 6 | `/email/config-status` | GET | Returns without error |
| 7 | `/tokens/summary` | GET | Returns without error |
| 8 | `/drive/sync` | POST | Files uploaded to Drive |

If all 8 pass, your system is fully operational.
