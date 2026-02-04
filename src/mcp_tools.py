"""
MCP Server Tools - Database, Filesystem, and External Integrations
Provides real database access, file operations, and external API calls
"""
import os
import sqlite3
import json
from typing import List, Dict, Any, Optional
from crewai_tools import tool
from pathlib import Path
import requests


# ============================================================================
# DATABASE MCP TOOLS
# ============================================================================

class DatabaseMCP:
    """MCP Server for Database Operations"""
    
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv(
            "DB_CONNECTION_STRING", 
            "sqlite:///./company.db"
        )
        self._setup_database()
    
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


# Global database instance
_db = None

def get_database() -> DatabaseMCP:
    """Get global database instance"""
    global _db
    if _db is None:
        _db = DatabaseMCP()
    return _db


@tool("Execute SQL Query")
def execute_sql_mcp_tool(query: str) -> str:
    """
    Execute SQL query on the company database
    
    Args:
        query: SQL query to execute (SELECT, INSERT, UPDATE, DELETE)
    
    Returns:
        JSON string with query results
    """
    try:
        db = get_database()
        results = db.execute_query(query)
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error executing query: {str(e)}"


@tool("Get Database Schema")
def get_db_schema_tool() -> str:
    """Get database schema information"""
    db = get_database()
    
    schema_query = """
        SELECT name, sql 
        FROM sqlite_master 
        WHERE type='table' 
        ORDER BY name
    """
    
    results = db.execute_query(schema_query)
    
    schema_info = "Database Schema:\n\n"
    for table in results:
        schema_info += f"Table: {table['name']}\n"
        schema_info += f"{table['sql']}\n\n"
    
    return schema_info


# ============================================================================
# FILESYSTEM MCP TOOLS
# ============================================================================

@tool("Read File")
def read_file_mcp_tool(filepath: str) -> str:
    """
    Read file contents from workspace
    
    Args:
        filepath: Path to file relative to workspace
    """
    workspace = os.getenv("AGENT_WORKSPACE", "./agent_workspace")
    full_path = os.path.join(workspace, filepath)
    
    try:
        if not os.path.exists(full_path):
            return f"File not found: {filepath}"
        
        with open(full_path, 'r') as f:
            content = f.read()
        
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool("Write File")
def write_file_mcp_tool(filepath: str, content: str) -> str:
    """
    Write content to file in workspace
    
    Args:
        filepath: Path to file relative to workspace
        content: Content to write
    """
    workspace = os.getenv("AGENT_WORKSPACE", "./agent_workspace")
    full_path = os.path.join(workspace, filepath)
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w') as f:
            f.write(content)
        
        return f"File written successfully: {filepath}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool("List Files")
def list_files_mcp_tool(directory: str = ".") -> str:
    """
    List files in workspace directory
    
    Args:
        directory: Directory path relative to workspace
    """
    workspace = os.getenv("AGENT_WORKSPACE", "./agent_workspace")
    full_path = os.path.join(workspace, directory)
    
    try:
        if not os.path.exists(full_path):
            return f"Directory not found: {directory}"
        
        files = []
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            files.append({
                "name": item,
                "type": "directory" if os.path.isdir(item_path) else "file",
                "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0
            })
        
        return json.dumps(files, indent=2)
    except Exception as e:
        return f"Error listing files: {str(e)}"


# ============================================================================
# JIRA MCP TOOLS (Real Integration)
# ============================================================================

class JiraMCP:
    """MCP Server for Jira Integration"""
    
    def __init__(self):
        self.base_url = os.getenv("JIRA_BASE_URL")
        self.email = os.getenv("JIRA_EMAIL")
        self.api_token = os.getenv("JIRA_API_TOKEN")
        self.enabled = all([self.base_url, self.email, self.api_token])
    
    def _get_headers(self):
        """Get authentication headers"""
        if not self.enabled:
            return {}
        
        import base64
        auth_str = f"{self.email}:{self.api_token}"
        auth_bytes = auth_str.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        return {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json"
        }
    
    def create_ticket(self, project_key: str, summary: str, description: str, 
                     issue_type: str = "Task") -> Dict:
        """Create Jira ticket"""
        if not self.enabled:
            return {"error": "Jira not configured"}
        
        url = f"{self.base_url}/rest/api/3/issue"
        
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": description}]
                        }
                    ]
                },
                "issuetype": {"name": issue_type}
            }
        }
        
        response = requests.post(url, json=payload, headers=self._get_headers())
        
        if response.status_code == 201:
            return response.json()
        else:
            return {"error": response.text}
    
    def update_ticket(self, ticket_key: str, status: str = None, 
                     comment: str = None) -> Dict:
        """Update Jira ticket"""
        if not self.enabled:
            return {"error": "Jira not configured"}
        
        result = {}
        
        # Update status
        if status:
            url = f"{self.base_url}/rest/api/3/issue/{ticket_key}/transitions"
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 200:
                transitions = response.json()['transitions']
                transition_id = next(
                    (t['id'] for t in transitions if t['name'].lower() == status.lower()),
                    None
                )
                
                if transition_id:
                    payload = {"transition": {"id": transition_id}}
                    requests.post(url, json=payload, headers=self._get_headers())
                    result['status_updated'] = True
        
        # Add comment
        if comment:
            url = f"{self.base_url}/rest/api/3/issue/{ticket_key}/comment"
            payload = {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": comment}]
                        }
                    ]
                }
            }
            
            response = requests.post(url, json=payload, headers=self._get_headers())
            result['comment_added'] = response.status_code == 201
        
        return result


_jira = None

def get_jira() -> JiraMCP:
    """Get global Jira instance"""
    global _jira
    if _jira is None:
        _jira = JiraMCP()
    return _jira


@tool("Create Jira Ticket")
def create_jira_ticket_tool(project_key: str, summary: str, description: str) -> str:
    """
    Create a Jira ticket
    
    Args:
        project_key: Jira project key (e.g., 'PROJ')
        summary: Ticket summary/title
        description: Detailed description
    """
    jira = get_jira()
    
    if not jira.enabled:
        # Fallback to simulated ticket
        ticket_id = f"{project_key}-{hash(summary) % 1000}"
        return json.dumps({
            "key": ticket_id,
            "summary": summary,
            "status": "Created (Simulated - Configure Jira for real integration)"
        }, indent=2)
    
    result = jira.create_ticket(project_key, summary, description)
    return json.dumps(result, indent=2)


@tool("Update Jira Ticket")
def update_jira_ticket_tool(ticket_key: str, status: str = None, comment: str = None) -> str:
    """
    Update Jira ticket status and/or add comment
    
    Args:
        ticket_key: Jira ticket key (e.g., 'PROJ-123')
        status: New status (optional)
        comment: Comment to add (optional)
    """
    jira = get_jira()
    
    if not jira.enabled:
        return json.dumps({
            "ticket": ticket_key,
            "status": "Updated (Simulated - Configure Jira for real integration)"
        }, indent=2)
    
    result = jira.update_ticket(ticket_key, status, comment)
    return json.dumps(result, indent=2)


# ============================================================================
# EMAIL MCP TOOLS
# ============================================================================

@tool("Send Email")
def send_email_mcp_tool(to: str, subject: str, body: str, cc: str = None) -> str:
    """
    Send email notification
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body
        cc: CC recipients (optional)
    """
    # Check if SMTP is configured
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    
    if all([smtp_host, smtp_port, smtp_user, smtp_pass]):
        # Real email sending
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        try:
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
            
            return f"Email sent successfully to {to}"
        except Exception as e:
            return f"Error sending email: {str(e)}"
    else:
        # Simulated email
        return json.dumps({
            "to": to,
            "subject": subject,
            "status": "Sent (Simulated - Configure SMTP for real emails)",
            "preview": body[:100] + "..."
        }, indent=2)


# ============================================================================
# WEB SEARCH MCP TOOLS
# ============================================================================

@tool("Web Search")
def web_search_mcp_tool(query: str, num_results: int = 5) -> str:
    """
    Search the web for information
    
    Args:
        query: Search query
        num_results: Number of results to return
    """
    api_key = os.getenv("SERP_API_KEY")
    
    if not api_key:
        return json.dumps({
            "query": query,
            "status": "Simulated - Configure SERP_API_KEY for real search",
            "results": [
                {"title": "Sample Result", "snippet": "This is a simulated search result"}
            ]
        }, indent=2)
    
    # Real search using SerpAPI
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": api_key,
        "num": num_results
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        results = []
        for result in data.get('organic_results', [])[:num_results]:
            results.append({
                "title": result.get('title'),
                "link": result.get('link'),
                "snippet": result.get('snippet')
            })
        
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error searching web: {str(e)}"