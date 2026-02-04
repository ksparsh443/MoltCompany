"""
FastAPI Server - AI Company API
Exposes endpoints to interact with the AI Company agents
"""
import os
import json
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import uvicorn
from dotenv import load_dotenv

from src.agents import create_crew
from src.memory_manager import get_memory_manager

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Company API",
    description="Multi-agent AI company that handles various business tasks",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Company crew (singleton)
ai_company = None

def get_ai_company():
    """Get or create AI Company crew instance"""
    global ai_company
    if ai_company is None:
        ai_company = create_crew()
    return ai_company


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class QueryRequest(BaseModel):
    """Request model for user queries"""
    query: str
    session_id: Optional[str] = None
    context: Optional[Dict] = None


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


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", response_model=dict)
async def root():
    """Root endpoint - API information"""
    return {
        "name": "AI Company API",
        "version": "1.0.0",
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
            "GET /knowledge/search": "Search knowledge base"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        company = get_ai_company()
        memory = get_memory_manager()
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            agents_loaded=6,
            memory_status="connected"
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, background_tasks: BackgroundTasks):
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
        # Generate session ID if not provided
        session_id = request.session_id or f"session_{int(datetime.utcnow().timestamp())}"
        
        # Get AI Company crew
        company = get_ai_company()
        
        # Process the query
        result = company.process_request(
            user_query=request.query,
            session_id=session_id
        )
        
        # Extract agents involved from result
        agents_involved = []
        if "AI Engineer" in result:
            agents_involved.append("AI Engineer")
        if "Data Analyst" in result:
            agents_involved.append("Data Analyst")
        if "PMO" in result:
            agents_involved.append("PMO")
        if "Security" in result:
            agents_involved.append("Security")
        if "DevOps" in result:
            agents_involved.append("DevOps")
        
        if not agents_involved:
            agents_involved = ["HR Manager"]
        
        return QueryResponse(
            status="success",
            result=result,
            session_id=session_id,
            agents_involved=agents_involved,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.get("/history/{session_id}")
async def get_history(session_id: str, limit: int = 10):
    """Get conversation history for a session"""
    try:
        memory = get_memory_manager()
        history = memory.get_conversation_history(session_id, limit)
        
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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge/search")
async def search_knowledge(query: str, limit: int = 5):
    """Search the company knowledge base"""
    try:
        memory = get_memory_manager()
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
    return {
        "agents": [
            {
                "name": "HR Manager",
                "role": "Orchestrator & Human Resources",
                "capabilities": [
                    "Route queries to appropriate agents",
                    "Recruit and hire employees",
                    "Schedule interviews",
                    "Manage employee records"
                ]
            },
            {
                "name": "Junior AI Engineer",
                "role": "AI Development & Automation",
                "capabilities": [
                    "Build AI agents",
                    "Create workflow automations",
                    "Generate Python code",
                    "Implement AI solutions"
                ]
            },
            {
                "name": "Data Analyst",
                "role": "Data Analysis & Business Intelligence",
                "capabilities": [
                    "ETL pipeline design",
                    "SQL query optimization",
                    "Data visualization",
                    "Business insights and reporting"
                ]
            },
            {
                "name": "PMO/Scrum Master",
                "role": "Project Management",
                "capabilities": [
                    "Project tracking (Jira/Azure DevOps)",
                    "Daily standups",
                    "Sprint planning",
                    "Status reporting"
                ]
            },
            {
                "name": "Security Pentester",
                "role": "Security Testing",
                "capabilities": [
                    "Penetration testing",
                    "Vulnerability scanning",
                    "Security audits",
                    "Compliance assessment"
                ]
            },
            {
                "name": "DevOps Engineer",
                "role": "Infrastructure & Deployment",
                "capabilities": [
                    "CI/CD pipeline creation",
                    "Infrastructure provisioning",
                    "Container orchestration",
                    "Cloud deployment"
                ]
            }
        ]
    }


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
    
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🏢 AI COMPANY API SERVER                              ║
    ║        Multi-Agent System                                    ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    🚀 Server starting on http://{host}:{port}
    📚 API Docs: http://{host}:{port}/docs
    📊 Alternative Docs: http://{host}:{port}/redoc
    
    Available Agents:
    ✅ HR Manager (Orchestrator)
    ✅ Junior AI Engineer
    ✅ Data Analyst
    ✅ PMO/Scrum Master
    ✅ Security Pentester
    ✅ DevOps Engineer
    
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
