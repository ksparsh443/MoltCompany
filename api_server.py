"""
FastAPI Server - AI Company API (Google ADK Edition)
Exposes endpoints to interact with the AI Company agents
"""

import os
import json
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
            "GET /agents/list": "List all agents and capabilities"
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
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🏢 AI COMPANY API SERVER (Google ADK)                 ║
    ║        Multi-Agent System v2.0                               ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝

    🚀 Server starting on http://{host}:{port}
    📚 API Docs: http://{host}:{port}/docs
    📊 Alternative Docs: http://{host}:{port}/redoc

    ⚙️  Configuration:
       Model Provider: {model_provider}
       Framework: Google ADK

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
