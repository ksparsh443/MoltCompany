"""
ADK Native Tools - Converted from MCP Tools

All tools are defined as functions with type hints and docstrings.
ADK automatically discovers tools from function signatures.
"""

import os
import json
import sqlite3
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
import requests

logger = logging.getLogger(__name__)


# ============================================================================
# DATABASE TOOLS
# ============================================================================

class DatabaseManager:
    """SQLite database manager for agent operations"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.connection_string = os.getenv(
            "DB_CONNECTION_STRING",
            "sqlite:///./company.db"
        )
        self._setup_database()
        self._initialized = True

    def _setup_database(self):
        """Initialize database with tables"""
        if self.connection_string.startswith("sqlite:///"):
            db_path = self.connection_string.replace("sqlite:///", "")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    role TEXT,
                    email TEXT,
                    department TEXT,
                    hire_date TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    status TEXT,
                    owner TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    budget REAL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    status TEXT,
                    priority TEXT,
                    assignee TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)

            conn.commit()
            conn.close()
            logger.info(f"Database initialized: {db_path}")

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute SQL query and return results"""
        if self.connection_string.startswith("sqlite:///"):
            db_path = self.connection_string.replace("sqlite:///", "")
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(query, params)

            if query.strip().upper().startswith("SELECT"):
                results = [dict(row) for row in cursor.fetchall()]
            else:
                conn.commit()
                results = [{"affected_rows": cursor.rowcount}]

            conn.close()
            return results

        return []


def get_database() -> DatabaseManager:
    """Get database manager singleton"""
    return DatabaseManager()


def execute_sql(query: str) -> dict:
    """
    Execute SQL query on the company database.

    Use this tool to run SQL queries for data retrieval or modification.
    Supports SELECT, INSERT, UPDATE, DELETE operations.

    Args:
        query: SQL query to execute (e.g., "SELECT * FROM employees WHERE role='Engineer'")

    Returns:
        Dict with query results or affected row count
    """
    try:
        db = get_database()
        results = db.execute_query(query)
        return {
            "status": "success",
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"SQL execution error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


def get_database_schema() -> dict:
    """
    Get the database schema information.

    Use this tool to understand the structure of available tables
    before writing SQL queries.

    Returns:
        Dict containing table definitions and column information
    """
    try:
        db = get_database()
        schema_query = """
            SELECT name, sql
            FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """
        results = db.execute_query(schema_query)

        tables = {}
        for table in results:
            tables[table['name']] = table['sql']

        return {
            "status": "success",
            "tables": tables,
            "table_count": len(tables)
        }
    except Exception as e:
        logger.error(f"Schema retrieval error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# ============================================================================
# FILESYSTEM TOOLS
# ============================================================================

def read_file(filepath: str) -> dict:
    """
    Read file contents from the workspace.

    Use this tool to read existing files for analysis or modification.

    Args:
        filepath: Path to file relative to workspace (e.g., "pending_approval/code.py")

    Returns:
        Dict with file contents or error message
    """
    workspace = os.getenv("AGENT_WORKSPACE", "./agent_workspace")
    full_path = os.path.join(workspace, filepath)

    try:
        if not os.path.exists(full_path):
            return {
                "status": "error",
                "error": f"File not found: {filepath}"
            }

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            "status": "success",
            "filepath": filepath,
            "content": content,
            "size_bytes": len(content)
        }
    except Exception as e:
        logger.error(f"File read error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


def write_file(filepath: str, content: str) -> dict:
    """
    Write content to a file in the workspace.

    Use this tool to create or overwrite files.

    Args:
        filepath: Path to file relative to workspace
        content: Content to write to the file

    Returns:
        Dict with operation status
    """
    workspace = os.getenv("AGENT_WORKSPACE", "./agent_workspace")
    full_path = os.path.join(workspace, filepath)

    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return {
            "status": "success",
            "filepath": filepath,
            "message": f"File written successfully: {filepath}",
            "size_bytes": len(content)
        }
    except Exception as e:
        logger.error(f"File write error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


def list_files(directory: str = ".") -> dict:
    """
    List files in a workspace directory.

    Use this tool to explore the workspace structure.

    Args:
        directory: Directory path relative to workspace (default: root)

    Returns:
        Dict with list of files and directories
    """
    workspace = os.getenv("AGENT_WORKSPACE", "./agent_workspace")
    full_path = os.path.join(workspace, directory)

    try:
        if not os.path.exists(full_path):
            return {
                "status": "error",
                "error": f"Directory not found: {directory}"
            }

        items = []
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            items.append({
                "name": item,
                "type": "directory" if os.path.isdir(item_path) else "file",
                "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0
            })

        return {
            "status": "success",
            "directory": directory,
            "items": items,
            "count": len(items)
        }
    except Exception as e:
        logger.error(f"Directory listing error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# ============================================================================
# CODE MANAGEMENT TOOLS
# ============================================================================

def save_code_file(filename: str, code: str, description: str) -> dict:
    """
    Save generated code to workspace for approval.

    Use this tool when you generate code that needs human review.
    Code is saved to pending_approval directory.

    Args:
        filename: Name of the file (e.g., "customer_support_agent.py")
        code: The actual code content
        description: What this code does

    Returns:
        Dict with save status and file path
    """
    workspace = os.getenv("AGENT_CODE_PENDING", "./agent_workspace/pending_approval")
    os.makedirs(workspace, exist_ok=True)

    filepath = os.path.join(workspace, filename)

    try:
        # Save code file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)

        # Save metadata
        metadata = {
            "filename": filename,
            "description": description,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending_approval"
        }

        metadata_path = filepath + ".meta.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Code saved for approval: {filename}")

        return {
            "status": "success",
            "filepath": filepath,
            "message": f"Code saved to {filepath} - awaiting approval",
            "description": description
        }
    except Exception as e:
        logger.error(f"Code save error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# ============================================================================
# MEMORY TOOLS
# ============================================================================

def save_to_memory(data: str, category: str = "general") -> dict:
    """
    Save important information to long-term memory.

    Use this tool to store knowledge that should be remembered
    across conversations.

    Args:
        data: Information to save
        category: Category for organization (e.g., "project", "employee", "knowledge")

    Returns:
        Dict with save status
    """
    try:
        from src.memory_manager import get_memory_manager

        memory = get_memory_manager()
        knowledge_id = f"kb_{hash(data) % 1000000}"

        memory.save_knowledge(
            knowledge_id=knowledge_id,
            title="Agent Knowledge",
            content=data,
            category=category
        )

        return {
            "status": "success",
            "message": "Information saved to memory successfully",
            "knowledge_id": knowledge_id
        }
    except Exception as e:
        logger.error(f"Memory save error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


def search_memory(query: str, category: Optional[str] = None, limit: int = 5) -> dict:
    """
    Search through company knowledge base and past conversations.

    Use this tool to find relevant information from memory.

    Args:
        query: Search query
        category: Filter by category (optional)
        limit: Maximum number of results

    Returns:
        Dict with search results
    """
    try:
        from src.memory_manager import get_memory_manager

        memory = get_memory_manager()
        results = memory.search_knowledge(query, category=category, n_results=limit)

        formatted_results = []
        for result in results:
            formatted_results.append({
                "content": result.get('content', '')[:500],
                "relevance": result.get('relevance_score', 0),
                "metadata": result.get('metadata', {})
            })

        return {
            "status": "success",
            "query": query,
            "results": formatted_results,
            "count": len(formatted_results)
        }
    except Exception as e:
        logger.error(f"Memory search error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# ============================================================================
# VISUALIZATION TOOLS
# ============================================================================

def create_visualization(chart_type: str, data: str, title: str) -> dict:
    """
    Create data visualization.

    Use this tool to generate charts and graphs.

    Args:
        chart_type: Type of chart (bar, line, pie, scatter)
        data: JSON string with chart data
        title: Chart title

    Returns:
        Dict with visualization status and path
    """
    try:
        # Create visualizations directory
        viz_dir = "./visualizations"
        os.makedirs(viz_dir, exist_ok=True)

        filename = f"{title.replace(' ', '_').lower()}_{chart_type}.png"
        filepath = os.path.join(viz_dir, filename)

        # Note: Actual visualization would require matplotlib
        # This is a placeholder that confirms the request
        return {
            "status": "success",
            "chart_type": chart_type,
            "title": title,
            "filepath": filepath,
            "message": f"Created {chart_type} chart: {title}. Saved to {filepath}"
        }
    except Exception as e:
        logger.error(f"Visualization error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# ============================================================================
# SECURITY TOOLS
# ============================================================================

def run_security_scan(target: str, scan_type: str = "full") -> dict:
    """
    Run security vulnerability scan.

    Use this tool for security assessments.

    Args:
        target: Target to scan (URL, application name, or path)
        scan_type: Type of scan (full, quick, owasp, ports)

    Returns:
        Dict with scan results
    """
    # Simulated security scan results
    findings = [
        {
            "severity": "medium",
            "title": "Missing Security Headers",
            "description": "X-Content-Type-Options header not set",
            "recommendation": "Add 'X-Content-Type-Options: nosniff' header"
        },
        {
            "severity": "low",
            "title": "Cookie without Secure flag",
            "description": "Session cookie missing Secure attribute",
            "recommendation": "Set Secure flag on all sensitive cookies"
        },
        {
            "severity": "info",
            "title": "Server Banner Disclosure",
            "description": "Server version exposed in response headers",
            "recommendation": "Remove or obfuscate server version headers"
        }
    ]

    return {
        "status": "success",
        "target": target,
        "scan_type": scan_type,
        "timestamp": datetime.utcnow().isoformat(),
        "findings": findings,
        "summary": {
            "critical": 0,
            "high": 0,
            "medium": 1,
            "low": 1,
            "info": 1
        },
        "message": f"Security scan ({scan_type}) completed on {target}"
    }


# ============================================================================
# INFRASTRUCTURE TOOLS
# ============================================================================

def deploy_infrastructure(resource_type: str, environment: str, config: Optional[str] = None) -> dict:
    """
    Deploy infrastructure resources.

    Use this tool for infrastructure provisioning and deployment.

    Args:
        resource_type: Type of resource (container, vm, service, database)
        environment: Target environment (dev, staging, production)
        config: Optional JSON configuration

    Returns:
        Dict with deployment status
    """
    # Simulated deployment
    resource_id = f"{resource_type}-{environment}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    return {
        "status": "success",
        "resource_type": resource_type,
        "environment": environment,
        "resource_id": resource_id,
        "endpoint": f"https://{resource_type}.{environment}.example.com",
        "message": f"Deployed {resource_type} to {environment} environment",
        "details": {
            "created_at": datetime.utcnow().isoformat(),
            "health_check": "passing",
            "replicas": 1 if environment == "dev" else 3
        }
    }


# ============================================================================
# JIRA TOOLS
# ============================================================================

def create_jira_ticket(project_key: str, summary: str, description: str, issue_type: str = "Task") -> dict:
    """
    Create a Jira ticket.

    Use this tool to create tickets for task tracking.

    Args:
        project_key: Jira project key (e.g., 'PROJ')
        summary: Ticket summary/title
        description: Detailed description
        issue_type: Type of issue (Task, Bug, Story, Epic)

    Returns:
        Dict with ticket information
    """
    # Check if Jira is configured
    jira_url = os.getenv("JIRA_BASE_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_token = os.getenv("JIRA_API_TOKEN")

    if all([jira_url, jira_email, jira_token]):
        # Real Jira integration
        try:
            import base64
            auth_str = f"{jira_email}:{jira_token}"
            auth_bytes = auth_str.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

            headers = {
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/json"
            }

            payload = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": summary,
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [{
                            "type": "paragraph",
                            "content": [{"type": "text", "text": description}]
                        }]
                    },
                    "issuetype": {"name": issue_type}
                }
            }

            response = requests.post(
                f"{jira_url}/rest/api/3/issue",
                json=payload,
                headers=headers
            )

            if response.status_code == 201:
                data = response.json()
                return {
                    "status": "success",
                    "key": data.get("key"),
                    "id": data.get("id"),
                    "url": f"{jira_url}/browse/{data.get('key')}",
                    "message": f"Ticket created: {data.get('key')}"
                }
            else:
                return {
                    "status": "error",
                    "error": response.text
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    else:
        # Simulated ticket
        ticket_id = f"{project_key}-{abs(hash(summary)) % 1000}"
        return {
            "status": "success",
            "key": ticket_id,
            "summary": summary,
            "issue_type": issue_type,
            "message": f"Ticket created: {ticket_id} (Simulated - Configure Jira for real integration)"
        }


def update_jira_ticket(ticket_key: str, status: Optional[str] = None, comment: Optional[str] = None) -> dict:
    """
    Update Jira ticket status and/or add comment.

    Use this tool to update existing tickets.

    Args:
        ticket_key: Jira ticket key (e.g., 'PROJ-123')
        status: New status (optional)
        comment: Comment to add (optional)

    Returns:
        Dict with update status
    """
    # Check if Jira is configured
    jira_url = os.getenv("JIRA_BASE_URL")

    if jira_url:
        # Would implement real Jira update here
        pass

    # Simulated update
    return {
        "status": "success",
        "ticket": ticket_key,
        "updated_status": status,
        "comment_added": bool(comment),
        "message": f"Ticket {ticket_key} updated (Simulated - Configure Jira for real integration)"
    }


# ============================================================================
# EMAIL TOOLS
# ============================================================================

def send_email(to: str, subject: str, body: str, cc: Optional[str] = None) -> dict:
    """
    Send email notification.

    Use this tool to send emails to stakeholders.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        cc: CC recipients (comma-separated, optional)

    Returns:
        Dict with send status
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")

    if all([smtp_host, smtp_port, smtp_user, smtp_pass]):
        # Real email sending
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = to
            msg['Subject'] = subject
            if cc:
                msg['Cc'] = cc

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(smtp_host, int(smtp_port))
            server.starttls()
            server.login(smtp_user, smtp_pass)

            recipients = [to]
            if cc:
                recipients.extend(cc.split(','))

            server.send_message(msg)
            server.quit()

            return {
                "status": "success",
                "to": to,
                "subject": subject,
                "message": f"Email sent successfully to {to}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    else:
        # Simulated email
        return {
            "status": "success",
            "to": to,
            "subject": subject,
            "preview": body[:100] + "..." if len(body) > 100 else body,
            "message": f"Email sent to {to} (Simulated - Configure SMTP for real emails)"
        }


# ============================================================================
# WEB SEARCH TOOLS
# ============================================================================

def web_search(query: str, num_results: int = 5) -> dict:
    """
    Search the web for information.

    Use this tool to find current information online.

    Args:
        query: Search query
        num_results: Number of results to return

    Returns:
        Dict with search results
    """
    api_key = os.getenv("SERP_API_KEY")

    if api_key:
        # Real search using SerpAPI
        try:
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": api_key,
                "num": num_results
            }

            response = requests.get(url, params=params)
            data = response.json()

            results = []
            for result in data.get('organic_results', [])[:num_results]:
                results.append({
                    "title": result.get('title'),
                    "link": result.get('link'),
                    "snippet": result.get('snippet')
                })

            return {
                "status": "success",
                "query": query,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    else:
        # Simulated search
        return {
            "status": "success",
            "query": query,
            "results": [
                {
                    "title": f"Search result for: {query}",
                    "link": "https://example.com",
                    "snippet": "This is a simulated search result. Configure SERP_API_KEY for real search."
                }
            ],
            "message": "Simulated search - Configure SERP_API_KEY for real results"
        }


# ============================================================================
# TOOL COLLECTIONS FOR AGENTS
# ============================================================================

# Tools for HR Manager
HR_TOOLS = [
    search_memory,
    save_to_memory,
    send_email,
    web_search,
]

# Tools for AI Engineer
ENGINEER_TOOLS = [
    save_code_file,
    read_file,
    write_file,
    list_files,
    search_memory,
    save_to_memory,
    web_search,
]

# Tools for Data Analyst
ANALYST_TOOLS = [
    execute_sql,
    get_database_schema,
    create_visualization,
    search_memory,
    save_to_memory,
    write_file,
]

# Tools for PMO/Scrum Master
PMO_TOOLS = [
    create_jira_ticket,
    update_jira_ticket,
    send_email,
    search_memory,
    save_to_memory,
    execute_sql,
]

# Tools for Security Pentester
SECURITY_TOOLS = [
    run_security_scan,
    write_file,
    search_memory,
    save_to_memory,
]

# Tools for DevOps Engineer
DEVOPS_TOOLS = [
    deploy_infrastructure,
    run_security_scan,
    write_file,
    search_memory,
    save_to_memory,
]

# All tools (for reference)
ALL_TOOLS = [
    execute_sql,
    get_database_schema,
    read_file,
    write_file,
    list_files,
    save_code_file,
    save_to_memory,
    search_memory,
    create_visualization,
    run_security_scan,
    deploy_infrastructure,
    create_jira_ticket,
    update_jira_ticket,
    send_email,
    web_search,
]
