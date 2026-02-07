"""
FastAPI Server - AI Company API (Google ADK Edition)
Exposes endpoints to interact with the AI Company agents
"""

import os
import json
import asyncio
import fastapi
from fastapi import FastAPI, HTTPException, BackgroundTasks, Form
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uvicorn
from dotenv import load_dotenv

# Load environment variables (.env overrides system env on Windows)
load_dotenv(override=True)

# Set PYTHONUTF8 for Windows compatibility
os.environ["PYTHONUTF8"] = "1"

from src.adk.runner import create_runner, AICompanyRunner
from src.adk.memory import get_memory_service

# Initialize FastAPI app
app = FastAPI(
    title="AI Company API",
    description="Multi-agent AI company powered by Google ADK with 6 specialist agents",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global runner instance (lazy loaded)
_ai_company: Optional[AICompanyRunner] = None


def get_ai_company() -> AICompanyRunner:
    """Get or create AI Company runner instance"""
    global _ai_company
    if _ai_company is None:
        _ai_company = create_runner()
    return _ai_company


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class QueryRequest(BaseModel):
    """Request model for user queries"""
    query: str
    session_id: Optional[str] = None
    user_id: Optional[str] = "default"
    stream: Optional[bool] = False


class QueryResponse(BaseModel):
    """Response model for query results"""
    status: str
    result: str
    session_id: str
    agents_involved: List[str]
    timestamp: str


class CodeApprovalRequest(BaseModel):
    """Request to approve or reject generated code"""
    filename: str
    approved: bool
    feedback: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    agents_loaded: int
    memory_status: str
    model_provider: str


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", response_model=dict)
async def root():
    """Root endpoint - API information"""
    return {
        "name": "AI Company API",
        "version": "2.0.0",
        "framework": "Google ADK",
        "description": "Multi-agent AI company with 6 specialist agents",
        "agents": [
            "HR Manager (Orchestrator)",
            "Junior AI Engineer",
            "Data Analyst",
            "PMO/Scrum Master",
            "Security Pentester",
            "DevOps Engineer"
        ],
        "endpoints": {
            "POST /query": "Submit a query to the AI company",
            "GET /health": "Health check",
            "GET /history/{session_id}": "Get conversation history",
            "GET /pending-code": "List code files pending approval",
            "POST /approve-code": "Approve or reject generated code",
            "GET /approved-code/{filename}": "Download approved code",
            "GET /knowledge/search": "Search knowledge base",
            "GET /agents/list": "List all agents and capabilities",
            "GET /drive/status": "Check Google Drive connection",
            "POST /drive/sync": "Force sync workspace to Drive",
            "GET /drive/folders": "List Drive folder structure",
            "GET /github/status": "Check GitHub connection"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        company = get_ai_company()
        memory = get_memory_service()
        model_provider = os.getenv("MODEL_PROVIDER", "gemini")

        return HealthResponse(
            status="healthy",
            version="2.0.0",
            agents_loaded=len(company.root_agent.sub_agents) + 1,
            memory_status="connected",
            model_provider=model_provider
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/query")
async def process_query(request: QueryRequest):
    """
    Main endpoint - Submit a query to the AI Company

    Example queries:
    - "Build me a customer support AI agent"
    - "Analyze our sales data and create a dashboard"
    - "Run security scan on our web application"
    - "Schedule interviews for 3 AI engineers"
    - "Deploy the new microservice to production"
    """
    try:
        company = get_ai_company()

        # Generate session ID if not provided
        session_id = request.session_id or f"session_{int(datetime.utcnow().timestamp())}"
        user_id = request.user_id or "default"

        if request.stream:
            # Streaming response
            async def generate():
                async for chunk in company.process_request_streaming(
                    query=request.query,
                    user_id=user_id,
                    session_id=session_id
                ):
                    yield f"data: {json.dumps(chunk)}\n\n"

            return StreamingResponse(
                generate(),
                media_type="text/event-stream"
            )
        else:
            # Regular response
            result = await company.process_request(
                query=request.query,
                user_id=user_id,
                session_id=session_id
            )

            if result["status"] == "error":
                raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))

            return QueryResponse(
                status=result["status"],
                result=result["result"],
                session_id=result["session_id"],
                agents_involved=result.get("agents_involved", ["HR_Manager"]),
                timestamp=result["timestamp"]
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.get("/history/{session_id}")
async def get_history(session_id: str, limit: int = 10):
    """Get conversation history for a session"""
    try:
        company = get_ai_company()
        history = company.get_conversation_history(session_id, limit)

        return {
            "session_id": session_id,
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pending-code")
async def list_pending_code():
    """List all code files pending approval"""
    try:
        pending_dir = os.getenv("AGENT_CODE_PENDING", "./agent_workspace/pending_approval")

        if not os.path.exists(pending_dir):
            return {"pending_files": [], "count": 0}

        files = []
        for filename in os.listdir(pending_dir):
            if filename.endswith('.meta.json'):
                continue

            filepath = os.path.join(pending_dir, filename)
            meta_path = filepath + ".meta.json"

            # Read metadata
            metadata = {}
            if os.path.exists(meta_path):
                with open(meta_path, 'r') as f:
                    metadata = json.load(f)

            # Read code preview
            with open(filepath, 'r') as f:
                code = f.read()
                preview = code[:500] + "..." if len(code) > 500 else code

            files.append({
                "filename": filename,
                "description": metadata.get("description", "No description"),
                "created_at": metadata.get("created_at", "Unknown"),
                "status": metadata.get("status", "pending"),
                "preview": preview,
                "size_bytes": len(code)
            })

        return {
            "pending_files": files,
            "count": len(files)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/approve-code")
async def approve_code(request: CodeApprovalRequest):
    """
    Approve or reject generated code

    If approved, moves code from pending to approved directory
    If rejected, deletes the code file
    """
    try:
        pending_dir = os.getenv("AGENT_CODE_PENDING", "./agent_workspace/pending_approval")
        approved_dir = os.getenv("AGENT_CODE_APPROVED", "./agent_workspace/approved")

        pending_path = os.path.join(pending_dir, request.filename)

        if not os.path.exists(pending_path):
            raise HTTPException(status_code=404, detail=f"File not found: {request.filename}")

        if request.approved:
            # Move to approved directory
            os.makedirs(approved_dir, exist_ok=True)
            approved_path = os.path.join(approved_dir, request.filename)

            os.rename(pending_path, approved_path)

            # Update metadata
            meta_path = pending_path + ".meta.json"
            if os.path.exists(meta_path):
                with open(meta_path, 'r') as f:
                    metadata = json.load(f)

                metadata['status'] = 'approved'
                metadata['approved_at'] = datetime.utcnow().isoformat()
                metadata['feedback'] = request.feedback

                approved_meta = approved_path + ".meta.json"
                with open(approved_meta, 'w') as f:
                    json.dump(metadata, f, indent=2)

                os.remove(meta_path)

            return {
                "status": "approved",
                "filename": request.filename,
                "message": f"Code approved and moved to {approved_path}"
            }
        else:
            # Delete file
            os.remove(pending_path)

            meta_path = pending_path + ".meta.json"
            if os.path.exists(meta_path):
                os.remove(meta_path)

            return {
                "status": "rejected",
                "filename": request.filename,
                "message": "Code rejected and deleted",
                "feedback": request.feedback
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/approved-code/{filename}")
async def download_approved_code(filename: str):
    """Download an approved code file"""
    try:
        approved_dir = os.getenv("AGENT_CODE_APPROVED", "./agent_workspace/approved")
        filepath = os.path.join(approved_dir, filename)

        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            filepath,
            media_type="text/plain",
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge/search")
async def search_knowledge(query: str, limit: int = 5):
    """Search the company knowledge base"""
    try:
        memory = get_memory_service()
        results = memory.search_knowledge(query, n_results=limit)

        return {
            "query": query,
            "results": results,
            "count": len(results)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/list")
async def list_agents():
    """List all available agents and their capabilities"""
    try:
        company = get_ai_company()
        return company.get_agents_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        company = get_ai_company()
        return company.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HR MANAGER ENDPOINTS
# ============================================================================

class CandidateSearchRequest(BaseModel):
    job_title: str
    skills: str = ""
    location: str = ""
    num_results: int = 10

class OnboardingRequest(BaseModel):
    employee_name: str
    email: str
    role: str
    department: str
    manager_email: str
    start_date: str

@app.post("/hr/search-candidates")
async def search_candidates(request: CandidateSearchRequest):
    """Search for candidates using LinkedIn/DuckDuckGo"""
    from src.adk.tools import search_linkedin_profiles
    result = search_linkedin_profiles(
        request.job_title, request.skills, request.location, request.num_results
    )
    return result

@app.post("/hr/onboard")
async def onboard_employee(request: OnboardingRequest):
    """Start invisible onboarding process"""
    from src.adk.tools import initiate_onboarding
    result = initiate_onboarding(
        request.employee_name, request.email, request.role,
        request.department, request.manager_email, request.start_date
    )
    return result

@app.get("/hr/employees")
async def list_employees(department: str = "", status: str = "active"):
    """List all employees"""
    from src.adk.tools import get_database
    db = get_database()
    if department:
        employees = db.execute_query(
            "SELECT * FROM employees WHERE department=? AND status=?",
            (department, status)
        )
    else:
        employees = db.execute_query(
            "SELECT * FROM employees WHERE status=?", (status,)
        )
    return {"employees": employees or [], "count": len(employees or [])}


# ============================================================================
# PMO/SCRUM MASTER ENDPOINTS
# ============================================================================

class TaskRequest(BaseModel):
    title: str
    description: str = ""
    project: str = ""
    assignee: str = ""
    priority: str = "medium"
    due_date: str = ""
    sprint: str = ""
    story_points: int = 0

class MeetingRequest(BaseModel):
    title: str
    meeting_type: str = "adhoc"
    scheduled_at: str
    duration_minutes: int = 60
    attendees: str
    agenda: str = ""

@app.post("/pmo/tasks")
async def create_new_task(request: TaskRequest):
    """Create a new task"""
    from src.adk.tools import create_task
    result = create_task(
        request.title, request.description, request.project,
        request.assignee, request.priority, request.due_date,
        request.sprint, request.story_points
    )
    return result

@app.get("/pmo/tasks")
async def get_all_tasks(project: str = "", sprint: str = "", status: str = ""):
    """Get tasks with optional filters"""
    from src.adk.tools import get_tasks
    result = get_tasks(project, sprint, "", status)
    return result

@app.post("/pmo/meetings")
async def schedule_new_meeting(request: MeetingRequest):
    """Schedule a meeting (generates ICS file)"""
    from src.adk.tools import schedule_meeting
    result = schedule_meeting(
        request.title, request.meeting_type, request.scheduled_at,
        request.duration_minutes, request.attendees, request.agenda
    )
    return result

@app.get("/pmo/meetings/{meeting_id}/ics")
async def download_meeting_ics(meeting_id: str):
    """Download ICS file for a meeting"""
    ics_path = f"./agent_workspace/pmo/meetings/{meeting_id}.ics"
    if os.path.exists(ics_path):
        return FileResponse(ics_path, media_type="text/calendar", filename=f"{meeting_id}.ics")
    raise HTTPException(status_code=404, detail="ICS file not found")

@app.post("/pmo/excel-tracker")
async def create_tracker(tracker_name: str, tracker_type: str = "sprint", project: str = ""):
    """Create Excel tracker"""
    from src.adk.tools import create_excel_tracker
    result = create_excel_tracker(tracker_name, tracker_type, project, "")
    return result


# ============================================================================
# SECURITY PENTESTER ENDPOINTS
# ============================================================================

class PentestRequest(BaseModel):
    target_url: str
    target_type: str = "web_application"
    scope: str = ""

class ScanRequest(BaseModel):
    session_id: str
    scan_type: str = "comprehensive"
    test_categories: List[str] = ["all"]

@app.post("/security/pentest/session")
async def create_pentest(request: PentestRequest):
    """Create a new pentest session"""
    from src.adk.tools import create_pentest_session
    result = create_pentest_session(request.target_url, request.target_type, request.scope)
    return result

@app.post("/security/pentest/scan")
async def run_scan(request: ScanRequest):
    """Run security scan on target"""
    from src.adk.tools import run_pentest_scan
    result = run_pentest_scan(request.session_id, request.scan_type, request.test_categories)
    return result

@app.get("/security/pentest/{session_id}/results")
async def get_pentest_results(session_id: str):
    """Get pentest results"""
    from src.adk.tools import get_pentest_results
    result = get_pentest_results(session_id)
    return result

@app.get("/security/pentest/{session_id}/report")
async def get_pentest_report(session_id: str, format: str = "markdown"):
    """Generate pentest report"""
    from src.adk.tools import generate_pentest_report
    result = generate_pentest_report(session_id, format)
    return result

@app.get("/security/sessions")
async def list_security_sessions(target_url: str = "", status: str = ""):
    """List all pentest sessions"""
    from src.adk.tools import list_pentest_sessions
    result = list_pentest_sessions(target_url, status)
    return result


# ============================================================================
# DATA ANALYST ENDPOINTS
# ============================================================================

class IngestRequest(BaseModel):
    file_path: str
    source_name: str = ""
    file_type: str = "auto"

class QueryDataRequest(BaseModel):
    source_id: str
    query: str
    query_type: str = "sql"

class ChartRequest(BaseModel):
    source_id: str
    chart_type: str
    x_column: str
    y_column: str
    title: str = ""
    color_column: str = ""
    aggregation: str = "none"

class DashboardRequest(BaseModel):
    title: str
    description: str = ""
    source_ids: str
    charts_config: str

@app.post("/data/ingest")
async def ingest_data(request: IngestRequest):
    """Ingest data file (CSV, XLSX, PDF, TXT)"""
    from src.adk.tools import ingest_data_file
    result = ingest_data_file(request.file_path, request.source_name, request.file_type)
    return result

@app.post("/data/query")
async def query_data_endpoint(request: QueryDataRequest):
    """Query data using SQL or RAG"""
    from src.adk.tools import query_data
    result = query_data(request.source_id, request.query, request.query_type)
    return result

@app.get("/data/catalog")
async def get_data_catalog_endpoint():
    """Get data catalog"""
    from src.adk.tools import get_data_catalog
    result = get_data_catalog()
    return result

@app.post("/data/chart")
async def create_chart(request: ChartRequest):
    """Create interactive chart"""
    from src.adk.tools import create_interactive_chart
    result = create_interactive_chart(
        request.source_id, request.chart_type, request.x_column,
        request.y_column, request.title, request.color_column, "", request.aggregation
    )
    return result

@app.post("/data/dashboard")
async def create_dashboard_endpoint(request: DashboardRequest):
    """Create Power BI-like dashboard"""
    from src.adk.tools import create_dashboard
    result = create_dashboard(
        request.title, request.description, request.source_ids, request.charts_config
    )
    return result

@app.get("/data/dashboards")
async def list_dashboards():
    """List all dashboards"""
    from src.adk.tools import get_dashboards
    result = get_dashboards()
    return result


# ============================================================================
# DATABASE & SYSTEM ENDPOINTS
# ============================================================================

@app.get("/db/status")
async def database_status():
    """Check database connection status with detailed diagnostics"""
    from src.adk.tools import get_database
    try:
        db = get_database()
        provider_info = db.get_provider_info()

        # Test query - use appropriate method for provider mode
        test_result = "failed"
        try:
            if provider_info.get("has_pg_connection"):
                result = db.execute_query("SELECT 1 as test")
                if result:
                    test_result = "passed"
            elif provider_info.get("supabase_connected"):
                # REST API mode - connection already verified during init
                test_result = "passed (REST API)"
            else:
                result = db.execute_query("SELECT 1 as test")
                if result:
                    test_result = "passed"
        except Exception as qe:
            test_result = f"failed: {qe}"

        is_connected = "passed" in test_result or provider_info.get("supabase_connected", False)

        return {
            "status": "connected" if is_connected else "error",
            "provider": provider_info["provider"],
            "mode": provider_info.get("mode", "unknown"),
            "supabase_connected": provider_info.get("supabase_connected", False),
            "has_pg_connection": provider_info.get("has_pg_connection", False),
            "test_query": test_result,
            "supabase_url": os.getenv("SUPABASE_URL", "not set")[:50] + "...",
            "db_url_configured": bool(os.getenv("SUPABASE_DB_URL")),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "provider": os.getenv("DB_PROVIDER", "unknown"),
            "hint": "Check SUPABASE_URL, SUPABASE_KEY, and SUPABASE_DB_URL in .env"
        }

@app.get("/db/schema")
async def get_schema():
    """Get database schema"""
    from src.adk.tools import get_database_schema
    result = get_database_schema()
    return result

@app.post("/email/test")
async def test_email(to_email: str, subject: str = "Test Email", body: str = "This is a test email from AI Company."):
    """Test email sending"""
    from src.adk.tools import send_email
    result = send_email(to_email, subject, body)
    return result

@app.get("/email/config-status")
async def email_config_status():
    """Check SMTP configuration status"""
    from src.adk.tools import _is_smtp_configured
    configured = _is_smtp_configured()
    return {
        "smtp_configured": configured,
        "smtp_host": os.getenv("SMTP_HOST", "not set"),
        "smtp_user": os.getenv("SMTP_USER", "not set")[:5] + "..." if os.getenv("SMTP_USER") else "not set",
        "message": "SMTP ready for real emails" if configured else "SMTP using placeholder credentials - emails will be simulated",
        "setup_steps": [
            "1. Go to https://myaccount.google.com",
            "2. Security -> 2-Step Verification -> Turn ON",
            "3. Go to https://myaccount.google.com/apppasswords",
            "4. Create App Password for 'Mail'",
            "5. Update SMTP_USER and SMTP_PASSWORD in .env"
        ] if not configured else []
    }


# ============================================================================
# TOKEN CONSUMPTION MONITORING ENDPOINTS
# ============================================================================

@app.get("/tokens/consumption")
async def get_token_usage(agent_name: str = "", model_name: str = "", days: int = 7, limit: int = 100):
    """Get token consumption data for monitoring - per agent, per model"""
    from src.adk.tools import get_token_consumption
    result = get_token_consumption(agent_name, model_name, days, limit)
    return result

@app.get("/tokens/summary")
async def get_token_summary():
    """Get real-time token consumption summary across all agents"""
    from src.adk.tools import get_token_logger
    logger_instance = get_token_logger()
    return {
        "status": "success",
        "agent_totals": logger_instance.get_agent_totals(),
        "session_totals": logger_instance.get_session_totals(),
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# MEETING RECORDER ENDPOINTS (Real-time Transcription)
# ============================================================================

class TranscriptChunk(BaseModel):
    meeting_id: str
    speaker: str = "Unknown"
    content: str
    confidence: float = 0.0

@app.post("/meetings/recording/start/{meeting_id}")
async def start_recording(meeting_id: str):
    """Start real-time meeting recording and transcription"""
    from src.adk.tools import start_meeting_recording
    result = start_meeting_recording(meeting_id)
    return result

@app.post("/meetings/recording/transcript")
async def add_transcript(chunk: TranscriptChunk):
    """Add a transcript chunk from the browser-based recorder"""
    from src.adk.tools import add_meeting_transcript
    result = add_meeting_transcript(chunk.meeting_id, chunk.speaker, chunk.content, chunk.confidence)
    return result

@app.post("/meetings/recording/stop/{meeting_id}")
async def stop_recording(meeting_id: str, auto_mom: bool = True):
    """Stop recording and optionally auto-generate MOM"""
    from src.adk.tools import stop_meeting_recording
    result = stop_meeting_recording(meeting_id, auto_mom)
    return result

@app.get("/meetings/recording/{meeting_id}/transcript")
async def get_transcript(meeting_id: str):
    """Get full transcript for a meeting"""
    from src.adk.tools import get_meeting_transcript
    result = get_meeting_transcript(meeting_id)
    return result

@app.get("/meetings/recording/active")
async def get_active_recordings():
    """Get all active recording sessions"""
    from src.adk.tools import get_meeting_recorder
    recorder = get_meeting_recorder()
    return recorder.get_active_recordings()

@app.get("/meeting-recorder")
async def meeting_recorder_page(meeting_id: str = ""):
    """
    Serve the meeting recorder HTML page.
    Uses Chrome's Web Speech API (FREE) for real-time transcription.
    Open this page alongside Google Meet to capture audio.
    """
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meeting Recorder - AI Company</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }}
        .header {{ text-align: center; padding: 20px; border-bottom: 1px solid #334155; margin-bottom: 20px; }}
        .header h1 {{ color: #38bdf8; font-size: 24px; }}
        .header p {{ color: #94a3b8; margin-top: 5px; }}
        .controls {{ display: flex; gap: 10px; justify-content: center; margin: 20px 0; flex-wrap: wrap; }}
        .btn {{ padding: 12px 24px; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; font-weight: 600; transition: all 0.2s; }}
        .btn-start {{ background: #22c55e; color: white; }}
        .btn-start:hover {{ background: #16a34a; }}
        .btn-stop {{ background: #ef4444; color: white; }}
        .btn-stop:hover {{ background: #dc2626; }}
        .btn-disabled {{ background: #475569; color: #94a3b8; cursor: not-allowed; }}
        .status {{ text-align: center; padding: 10px; margin: 10px 0; border-radius: 8px; }}
        .status-recording {{ background: #7f1d1d; border: 1px solid #ef4444; }}
        .status-idle {{ background: #1e3a5f; border: 1px solid #3b82f6; }}
        .config {{ background: #1e293b; padding: 15px; border-radius: 8px; margin: 15px 0; display: flex; gap: 15px; flex-wrap: wrap; align-items: center; }}
        .config label {{ color: #94a3b8; }}
        .config input {{ padding: 8px 12px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #e2e8f0; font-size: 14px; }}
        .transcript-box {{ background: #1e293b; border-radius: 8px; padding: 20px; margin-top: 15px; max-height: 500px; overflow-y: auto; }}
        .transcript-entry {{ padding: 8px 12px; margin: 5px 0; border-left: 3px solid #3b82f6; background: #0f172a; border-radius: 0 6px 6px 0; }}
        .transcript-entry .time {{ color: #64748b; font-size: 12px; }}
        .transcript-entry .speaker {{ color: #38bdf8; font-weight: 600; }}
        .transcript-entry .text {{ color: #e2e8f0; margin-top: 3px; }}
        .stats {{ display: flex; gap: 20px; justify-content: center; margin: 15px 0; }}
        .stat {{ background: #1e293b; padding: 12px 20px; border-radius: 8px; text-align: center; }}
        .stat .value {{ font-size: 24px; font-weight: 700; color: #38bdf8; }}
        .stat .label {{ color: #94a3b8; font-size: 12px; }}
        .interim {{ color: #64748b; font-style: italic; padding: 5px 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Meeting Recorder</h1>
        <p>Real-time transcription using Chrome Speech Recognition (FREE)</p>
    </div>

    <div class="config">
        <label>Meeting ID:</label>
        <input type="text" id="meetingId" value="{meeting_id}" placeholder="MTG-20260207..." size="30">
        <label>Your Name:</label>
        <input type="text" id="speakerName" placeholder="Your Name" size="20">
        <label>Language:</label>
        <select id="language" style="padding: 8px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #e2e8f0;">
            <option value="en-US">English (US)</option>
            <option value="en-GB">English (UK)</option>
            <option value="hi-IN">Hindi</option>
            <option value="es-ES">Spanish</option>
            <option value="fr-FR">French</option>
            <option value="de-DE">German</option>
        </select>
    </div>

    <div class="controls">
        <button class="btn btn-start" id="btnStart" onclick="startRecording()">Start Recording</button>
        <button class="btn btn-stop btn-disabled" id="btnStop" onclick="stopRecording()" disabled>Stop Recording</button>
    </div>

    <div class="status status-idle" id="status">Ready to record. Click "Start Recording" to begin.</div>

    <div class="stats">
        <div class="stat"><div class="value" id="segmentCount">0</div><div class="label">Segments</div></div>
        <div class="stat"><div class="value" id="duration">00:00</div><div class="label">Duration</div></div>
        <div class="stat"><div class="value" id="wordCount">0</div><div class="label">Words</div></div>
    </div>

    <div id="interim" class="interim"></div>
    <div class="transcript-box" id="transcriptBox">
        <p style="color: #64748b; text-align: center;">Transcripts will appear here...</p>
    </div>

    <script>
        const API_BASE = window.location.origin;
        let recognition = null;
        let isRecording = false;
        let startTime = null;
        let segmentCount = 0;
        let totalWords = 0;
        let durationInterval = null;

        function startRecording() {{
            const meetingId = document.getElementById('meetingId').value.trim();
            if (!meetingId) {{ alert('Please enter a Meeting ID'); return; }}

            // Start server-side recording
            fetch(API_BASE + '/meetings/recording/start/' + meetingId, {{ method: 'POST' }})
                .then(r => r.json())
                .then(data => {{
                    if (data.status === 'success') {{
                        startSpeechRecognition();
                    }} else {{
                        alert('Failed to start recording: ' + (data.error || 'Unknown error'));
                    }}
                }})
                .catch(err => {{
                    console.error(err);
                    // Start anyway for local testing
                    startSpeechRecognition();
                }});
        }}

        function startSpeechRecognition() {{
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
                alert('Speech Recognition not supported. Please use Chrome.');
                return;
            }}

            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = document.getElementById('language').value;

            recognition.onresult = function(event) {{
                let interim = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {{
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {{
                        sendTranscript(transcript, event.results[i][0].confidence);
                    }} else {{
                        interim += transcript;
                    }}
                }}
                document.getElementById('interim').textContent = interim ? 'Hearing: ' + interim : '';
            }};

            recognition.onend = function() {{
                if (isRecording) recognition.start();
            }};

            recognition.onerror = function(event) {{
                console.error('Speech error:', event.error);
                if (event.error === 'no-speech' && isRecording) recognition.start();
            }};

            recognition.start();
            isRecording = true;
            startTime = new Date();
            durationInterval = setInterval(updateDuration, 1000);

            document.getElementById('btnStart').classList.add('btn-disabled');
            document.getElementById('btnStart').disabled = true;
            document.getElementById('btnStop').classList.remove('btn-disabled');
            document.getElementById('btnStop').disabled = false;
            document.getElementById('status').className = 'status status-recording';
            document.getElementById('status').textContent = 'Recording in progress... Speak clearly.';
            document.getElementById('transcriptBox').innerHTML = '';
        }}

        function sendTranscript(text, confidence) {{
            const meetingId = document.getElementById('meetingId').value.trim();
            const speaker = document.getElementById('speakerName').value.trim() || 'Unknown';

            segmentCount++;
            totalWords += text.split(/\\s+/).length;
            document.getElementById('segmentCount').textContent = segmentCount;
            document.getElementById('wordCount').textContent = totalWords;

            // Add to UI
            const box = document.getElementById('transcriptBox');
            const entry = document.createElement('div');
            entry.className = 'transcript-entry';
            const now = new Date().toLocaleTimeString();
            entry.innerHTML = '<span class="time">' + now + '</span> <span class="speaker">' + speaker + '</span><div class="text">' + text + '</div>';
            box.appendChild(entry);
            box.scrollTop = box.scrollHeight;

            // Send to server
            fetch(API_BASE + '/meetings/recording/transcript', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ meeting_id: meetingId, speaker: speaker, content: text, confidence: confidence }})
            }}).catch(err => console.error('Send failed:', err));
        }}

        function stopRecording() {{
            isRecording = false;
            if (recognition) recognition.stop();
            if (durationInterval) clearInterval(durationInterval);

            const meetingId = document.getElementById('meetingId').value.trim();
            fetch(API_BASE + '/meetings/recording/stop/' + meetingId + '?auto_mom=true', {{ method: 'POST' }})
                .then(r => r.json())
                .then(data => {{
                    document.getElementById('status').className = 'status status-idle';
                    document.getElementById('status').textContent = 'Recording stopped. ' + (data.transcript_count || 0) + ' segments captured.' +
                        (data.auto_mom ? ' MOM auto-generated: ' + data.auto_mom.mom_id : '');
                }})
                .catch(err => {{
                    document.getElementById('status').className = 'status status-idle';
                    document.getElementById('status').textContent = 'Recording stopped locally. Server sync may have failed.';
                }});

            document.getElementById('btnStart').classList.remove('btn-disabled');
            document.getElementById('btnStart').disabled = false;
            document.getElementById('btnStop').classList.add('btn-disabled');
            document.getElementById('btnStop').disabled = true;
            document.getElementById('interim').textContent = '';
        }}

        function updateDuration() {{
            if (!startTime) return;
            const elapsed = Math.floor((new Date() - startTime) / 1000);
            const mins = String(Math.floor(elapsed / 60)).padStart(2, '0');
            const secs = String(elapsed % 60).padStart(2, '0');
            document.getElementById('duration').textContent = mins + ':' + secs;
        }}
    </script>
</body>
</html>"""
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)


# ============================================================================
# DESIGNATION EMAIL MANAGEMENT ENDPOINTS
# ============================================================================

class DesignationRequest(BaseModel):
    designation: str
    email: str
    name: str = ""

@app.post("/designations/set")
async def set_designation(request: DesignationRequest):
    """Map a designation/role to an email address for notifications"""
    from src.adk.tools import set_designation_email
    result = set_designation_email(request.designation, request.email, request.name)
    return result

@app.get("/designations/resolve/{designation}")
async def resolve_designation(designation: str):
    """Resolve a designation to its email address"""
    from src.adk.tools import get_designation_email
    email = get_designation_email(designation)
    if email:
        return {"designation": designation, "email": email, "status": "found"}
    return {"designation": designation, "email": None, "status": "not_found"}

@app.post("/designations/notify")
async def notify_designation(designation: str, subject: str, body: str):
    """Send notification to a designation/role"""
    from src.adk.tools import notify_by_designation
    result = notify_by_designation(designation, subject, body)
    return result


# ============================================================================
# GOOGLE DRIVE SYNC ENDPOINTS
# ============================================================================

@app.get("/drive/status")
async def drive_status():
    """Check Google Drive integration status and recent uploads"""
    from src.adk.tools import get_drive_status
    return get_drive_status()

@app.post("/drive/reload")
async def drive_reload():
    """Re-read .env and reconnect Google Drive (call after config changes)"""
    from src.adk.tools import get_drive_manager
    dm = get_drive_manager()
    return dm.reload()

@app.post("/drive/sync")
async def drive_sync():
    """Force-sync all workspace files to Google Drive"""
    from src.adk.tools import sync_workspace_to_drive
    result = sync_workspace_to_drive()
    return result

@app.get("/drive/folders")
async def drive_folders():
    """List the Google Drive folder structure"""
    from src.adk.tools import get_drive_manager
    dm = get_drive_manager()
    return dm.get_folder_structure()


# ============================================================================
# LINKEDIN EASY SETUP (OAuth Flow - just click through browser)
# ============================================================================

@app.get("/linkedin/setup")
async def linkedin_setup_page():
    """
    One-page LinkedIn setup wizard.
    Visit http://localhost:8000/linkedin/setup in your browser.
    """
    client_id = os.getenv("LINKEDIN_CLIENT_ID", "")
    client_secret_val = os.getenv("LINKEDIN_CLIENT_SECRET", "")
    has_token = bool(os.getenv("LINKEDIN_ACCESS_TOKEN", "").strip())
    has_urn = bool(os.getenv("LINKEDIN_PERSON_URN", "").strip())

    # Build conditional parts outside f-string to avoid backslash issues
    if has_token and has_urn:
        status_class = "ok"
        status_msg = "LinkedIn is READY - token and URN configured!"
    elif client_id:
        status_class = "warn"
        status_msg = "Partially configured - follow the steps below"
    else:
        status_class = "err"
        status_msg = "Not configured yet - follow the steps below"

    done_section = ""
    if has_token and has_urn:
        done_section = (
            '<div class="step"><h3>All Done!</h3>'
            "<p>Your LinkedIn is connected. Test it:</p>"
            '<pre style="background:#0f172a;padding:10px;border-radius:4px;margin-top:8px;overflow-x:auto">'
            "<code>POST http://localhost:8000/marketing/post\n"
            '{"content":"Hello from AI Company!","platforms":"linkedin"}</code></pre></div>'
        )

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>LinkedIn Setup - AI Company</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:-apple-system,sans-serif; background:#0f172a; color:#e2e8f0; padding:40px; max-width:800px; margin:0 auto; }}
  h1 {{ color:#38bdf8; margin-bottom:10px; }}
  .status {{ padding:12px 20px; border-radius:8px; margin:15px 0; }}
  .ok {{ background:#14532d; border:1px solid #22c55e; }}
  .warn {{ background:#713f12; border:1px solid #f59e0b; }}
  .err {{ background:#7f1d1d; border:1px solid #ef4444; }}
  .step {{ background:#1e293b; padding:20px; border-radius:8px; margin:15px 0; border-left:4px solid #3b82f6; }}
  .step h3 {{ color:#38bdf8; margin-bottom:8px; }}
  .step p {{ color:#94a3b8; line-height:1.6; }}
  code {{ background:#334155; padding:2px 8px; border-radius:4px; font-size:14px; }}
  a {{ color:#38bdf8; }}
  .btn {{ display:inline-block; padding:12px 24px; background:#3b82f6; color:white; border-radius:8px; text-decoration:none; font-weight:600; margin:10px 5px; }}
  .btn:hover {{ background:#2563eb; }}
  .btn-green {{ background:#22c55e; }}
  .btn-green:hover {{ background:#16a34a; }}
  input {{ padding:10px; border-radius:6px; border:1px solid #475569; background:#0f172a; color:#e2e8f0; width:100%; margin:5px 0; font-size:14px; }}
  .form-group {{ margin:10px 0; }}
  label {{ color:#94a3b8; font-size:14px; }}
</style></head><body>
<h1>LinkedIn Setup Wizard</h1>
<p style="color:#94a3b8">Get LinkedIn posting working in 3 minutes</p>

<div class="status {status_class}">{status_msg}</div>

<div class="step">
  <h3>Step 1: Create a Company Page (30 seconds)</h3>
  <p>LinkedIn requires this to create an app. It is just a formality - you will never use it.</p>
  <p><br>1. Go to <a href="https://www.linkedin.com/company/setup/new/" target="_blank">linkedin.com/company/setup/new/</a><br>
  2. Pick <b>"Small business"</b><br>
  3. Name: anything (e.g. "My AI Lab") - URL: anything unique<br>
  4. Check the box, click <b>Create page</b> - Done! Never touch it again.</p>
</div>

<div class="step">
  <h3>Step 2: Create LinkedIn App (1 minute)</h3>
  <p>1. Go to <a href="https://www.linkedin.com/developers/apps/new" target="_blank">linkedin.com/developers/apps/new</a><br>
  2. App name: <code>AI Company</code> - Company: select page from Step 1<br>
  3. Logo: any image - Check terms - <b>Create app</b><br>
  4. <b>Settings tab</b> - Click <b>Verify</b> next to your company page<br>
  5. <b>Products tab</b> - Request <b>"Share on LinkedIn"</b> (instant) + <b>"Sign In with LinkedIn using OpenID Connect"</b><br>
  6. <b>Auth tab</b> - Add redirect URL: <code>http://localhost:8000/linkedin/callback</code><br>
  7. Copy <b>Client ID</b> and <b>Client Secret</b> from the Auth tab</p>
</div>

<div class="step">
  <h3>Step 3: Enter Credentials and Authorize</h3>
  <form method="POST" action="/linkedin/save-credentials">
    <div class="form-group">
      <label>Client ID (from Auth tab):</label>
      <input type="text" name="client_id" value="{client_id}" placeholder="e.g. 86abc123def456" required>
    </div>
    <div class="form-group">
      <label>Client Secret (from Auth tab):</label>
      <input type="password" name="client_secret" value="{client_secret_val}" placeholder="e.g. WPLs8k..." required>
    </div>
    <button type="submit" class="btn btn-green">Save and Authorize with LinkedIn</button>
  </form>
</div>

{done_section}

</body></html>"""
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html)


@app.post("/linkedin/save-credentials")
async def linkedin_save_credentials(client_id: str = Form(...), client_secret: str = Form(...)):
    """Save LinkedIn Client ID/Secret and redirect to OAuth"""
    from fastapi.responses import RedirectResponse

    if not client_id or not client_secret:
        raise HTTPException(status_code=400, detail="Client ID and Client Secret are required")

    # Save to .env
    _update_env_var("LINKEDIN_CLIENT_ID", client_id)
    _update_env_var("LINKEDIN_CLIENT_SECRET", client_secret)

    # Reload env
    load_dotenv(override=True)

    # Redirect to LinkedIn OAuth
    redirect_uri = "http://localhost:8000/linkedin/callback"
    scopes = "openid%20w_member_social%20profile"
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scopes}"
    )
    return RedirectResponse(url=auth_url, status_code=302)


@app.get("/linkedin/callback")
async def linkedin_callback(code: str = "", error: str = ""):
    """OAuth callback - exchanges code for token and fetches Person URN"""
    from fastapi.responses import HTMLResponse
    import requests as req

    if error:
        return HTMLResponse(content=f"<h1>LinkedIn Error</h1><p>{error}</p><a href='/linkedin/setup'>Try again</a>")

    if not code:
        return HTMLResponse(content="<h1>Error</h1><p>No authorization code received</p><a href='/linkedin/setup'>Try again</a>")

    client_id = os.getenv("LINKEDIN_CLIENT_ID", "")
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "")
    redirect_uri = "http://localhost:8000/linkedin/callback"

    # Exchange code for access token
    try:
        token_resp = req.post("https://www.linkedin.com/oauth/v2/accessToken", data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        }, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=15)

        if token_resp.status_code != 200:
            return HTMLResponse(content=f"<h1>Token Error</h1><pre>{token_resp.text}</pre><a href='/linkedin/setup'>Try again</a>")

        token_data = token_resp.json()
        access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 5184000)  # default 60 days

    except Exception as e:
        return HTMLResponse(content=f"<h1>Token Exchange Failed</h1><p>{e}</p><a href='/linkedin/setup'>Try again</a>")

    # Fetch Person URN via userinfo
    try:
        userinfo_resp = req.get("https://api.linkedin.com/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}, timeout=10)

        if userinfo_resp.status_code == 200:
            person_urn = userinfo_resp.json().get("sub", "")
            user_name = userinfo_resp.json().get("name", "Unknown")
        else:
            return HTMLResponse(content=f"<h1>Userinfo Error</h1><pre>{userinfo_resp.text}</pre><a href='/linkedin/setup'>Try again</a>")
    except Exception as e:
        return HTMLResponse(content=f"<h1>Userinfo Failed</h1><p>{e}</p><a href='/linkedin/setup'>Try again</a>")

    # Save to .env
    _update_env_var("LINKEDIN_ACCESS_TOKEN", access_token)
    _update_env_var("LINKEDIN_PERSON_URN", person_urn)

    # Reload env so the app picks it up immediately
    load_dotenv(override=True)

    import math
    days = math.ceil(expires_in / 86400)

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>LinkedIn Connected!</title>
<style>
  body {{ font-family:-apple-system,sans-serif; background:#0f172a; color:#e2e8f0; padding:40px; max-width:700px; margin:0 auto; text-align:center; }}
  h1 {{ color:#22c55e; font-size:36px; margin:20px 0; }}
  .card {{ background:#1e293b; padding:25px; border-radius:12px; margin:20px 0; text-align:left; }}
  .card p {{ margin:8px 0; color:#94a3b8; }}
  .card b {{ color:#e2e8f0; }}
  code {{ background:#334155; padding:2px 8px; border-radius:4px; }}
  .btn {{ display:inline-block; padding:14px 28px; background:#3b82f6; color:white; border-radius:8px; text-decoration:none; font-weight:600; margin:10px; }}
  pre {{ background:#0f172a; padding:12px; border-radius:6px; overflow-x:auto; text-align:left; font-size:13px; }}
</style></head><body>
<h1>LinkedIn Connected!</h1>
<p style="font-size:18px">You're all set, {user_name}!</p>

<div class="card">
  <p><b>Person URN:</b> <code>{person_urn}</code></p>
  <p><b>Token expires in:</b> ~{days} days</p>
  <p><b>Saved to:</b> .env (auto-loaded)</p>
</div>

<div class="card">
  <p><b>Test it now:</b></p>
  <pre><code>curl -X POST http://localhost:8000/marketing/post \\
  -H "Content-Type: application/json" \\
  -d '{{"content":"Hello LinkedIn from AI Company!","platforms":"linkedin"}}'</code></pre>
</div>

<a class="btn" href="/linkedin/setup">Back to Setup</a>
<a class="btn" href="/docs">API Docs</a>
</body></html>"""
    return HTMLResponse(content=html)


def _update_env_var(key: str, value: str):
    """Update or add a variable in the .env file"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        # Try project root
        env_path = ".env"

    lines = []
    found = False
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.strip().startswith(f"{key}=") or line.strip().startswith(f"{key} ="):
            new_lines.append(f"{key}={value}\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{key}={value}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    # Also set in current process
    os.environ[key] = value


# ============================================================================
# MARKETING ENDPOINTS (Image Gen, Social Posting, Video Gen)
# ============================================================================

class ImageGenRequest(BaseModel):
    prompt: str
    style: str = "professional"
    size: str = "1024x1024"
    platform: str = "linkedin"

class SocialPostRequest(BaseModel):
    content: str
    platforms: str = "linkedin"
    image_path: str = ""
    hashtags: str = ""
    visibility: str = "PUBLIC"

class VideoGenRequest(BaseModel):
    prompt: str
    duration: int = 5
    style: str = "professional"
    method: str = "slideshow"

class AutoLinkedInRequest(BaseModel):
    topic: str
    tone: str = "professional"
    generate_image: bool = True
    image_style: str = "professional"
    post_immediately: bool = True
    visibility: str = "PUBLIC"

class EnhancePostRequest(BaseModel):
    content: str
    platform: str = "linkedin"
    tone: str = "professional"
    add_hashtags: bool = True
    add_hook: bool = True
    add_cta: bool = True

@app.post("/marketing/auto-linkedin")
async def marketing_auto_linkedin(request: AutoLinkedInRequest):
    """
    Fully automated LinkedIn post: AI writes content + generates hashtags + creates image + posts.
    One API call does everything end-to-end.
    """
    from src.adk.tools import auto_create_linkedin_post
    result = auto_create_linkedin_post(
        request.topic, request.tone, request.generate_image,
        request.image_style, request.post_immediately, request.visibility
    )
    return result

@app.post("/marketing/enhance")
async def marketing_enhance_post(request: EnhancePostRequest):
    """Use AI to add hashtags, hooks, and CTAs to any post content"""
    from src.adk.tools import enhance_post_with_ai
    result = enhance_post_with_ai(
        request.content, request.platform, request.tone,
        request.add_hashtags, request.add_hook, request.add_cta
    )
    return result

@app.post("/marketing/generate-image")
async def marketing_generate_image(request: ImageGenRequest):
    """Generate a marketing image using HuggingFace (FREE)"""
    from src.adk.tools import generate_marketing_image
    result = generate_marketing_image(
        request.prompt, request.style, request.size, request.platform
    )
    return result

@app.post("/marketing/post")
async def marketing_post(request: SocialPostRequest):
    """Post to LinkedIn/Twitter (or save as ready-to-copy if not configured)"""
    from src.adk.tools import post_to_social
    result = post_to_social(
        request.content, request.platforms, request.image_path, request.hashtags
    )
    return result

@app.post("/marketing/generate-video")
async def marketing_generate_video(request: VideoGenRequest):
    """Generate a marketing video (slideshow or HuggingFace model)"""
    from src.adk.tools import generate_marketing_video
    result = generate_marketing_video(
        request.prompt, request.duration, request.style, request.method
    )
    return result

@app.get("/marketing/assets")
async def marketing_list_assets(asset_type: str = "all"):
    """List all marketing assets (images, videos, posts)"""
    from src.adk.tools import list_marketing_assets
    result = list_marketing_assets(asset_type)
    return result

@app.get("/marketing/assets/{asset_type}/{filename}")
async def marketing_download_asset(asset_type: str, filename: str):
    """Download a specific marketing asset file"""
    workspace = os.getenv("AGENT_WORKSPACE", "./agent_workspace")
    filepath = os.path.join(workspace, "marketing", asset_type, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"Asset not found: {asset_type}/{filename}")

    # Determine media type
    media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".mp4": "video/mp4",
        ".txt": "text/plain",
    }
    ext = os.path.splitext(filename)[1].lower()
    media_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(filepath, media_type=media_type, filename=filename)


# ============================================================================
# GITHUB INTEGRATION ENDPOINTS
# ============================================================================

@app.get("/github/status")
async def github_status():
    """Check GitHub connection status and token validity"""
    from src.adk.tools import get_github_status
    return get_github_status()


# ============================================================================
# RUN SERVER
# ============================================================================

def start_server(
    host: str = None,
    port: int = None,
    reload: bool = False
):
    """Start the FastAPI server"""
    host = host or os.getenv("API_HOST", "0.0.0.0")
    port = port or int(os.getenv("API_PORT", 8000))
    model_provider = os.getenv("MODEL_PROVIDER", "gemini")

    print(f"""
    ==============================================================
    |                                                              |
    |        AI COMPANY API SERVER (Google ADK)                    |
    |        Multi-Agent System v2.0                               |
    |                                                              |
    ==============================================================

    Server starting on http://{host}:{port}
    API Docs: http://{host}:{port}/docs
    Alternative Docs: http://{host}:{port}/redoc

    Configuration:
       Model Provider: {model_provider}
       Framework: Google ADK

    Available Agents:
    [+] HR Manager (Orchestrator)
    [+] Junior AI Engineer
    [+] Data Analyst
    [+] PMO/Scrum Master
    [+] Security Pentester
    [+] DevOps Engineer
    [+] Sales & Marketing

    Press Ctrl+C to stop the server
    """)

    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    start_server(reload=True)
