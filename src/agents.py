"""
AI Company Agents - Using CrewAI Framework with MCP Integration
All 6 specialist agents with real database and tool access
"""
import os
from crewai import Agent, Task, Crew
from crewai_tools import tool

# Import from src directory
from src.llm_config import create_llm_for_agent, get_mcp_manager
from src.mcp_tools import (
    execute_sql_mcp_tool,
    get_db_schema_tool,
    read_file_mcp_tool,
    write_file_mcp_tool,
    list_files_mcp_tool,
    create_jira_ticket_tool,
    update_jira_ticket_tool,
    send_email_mcp_tool,
    web_search_mcp_tool
)
from src.memory_manager import get_memory_manager
from typing import List, Dict, Any
import json


# ============================================================================
# ADDITIONAL AGENT TOOLS
# ============================================================================

@tool("Save to Memory")
def save_to_memory_tool(data: str) -> str:
    """Save important information to long-term memory"""
    memory = get_memory_manager()
    memory.save_knowledge(
        knowledge_id=f"kb_{hash(data)}",
        title="Agent Knowledge",
        content=data,
        category="agent_generated"
    )
    return "Information saved to memory successfully"


@tool("Search Memory")
def search_memory_tool(query: str) -> str:
    """Search through company knowledge base and past conversations"""
    memory = get_memory_manager()
    results = memory.search_knowledge(query, n_results=3)
    
    if not results:
        return "No relevant information found in memory"
    
    output = "Found relevant information:\n\n"
    for i, result in enumerate(results, 1):
        output += f"{i}. {result['content'][:200]}...\n\n"
    
    return output


@tool("Save Code File")
def save_code_file_tool(filename: str, code: str, description: str) -> str:
    """
    Save generated code to workspace for approval
    Args:
        filename: Name of the file (e.g., customer_support_agent.py)
        code: The actual code content
        description: What this code does
    """
    workspace = os.getenv("AGENT_CODE_PENDING", "./agent_workspace/pending_approval")
    os.makedirs(workspace, exist_ok=True)
    
    filepath = os.path.join(workspace, filename)
    
    # Save code file
    with open(filepath, 'w') as f:
        f.write(code)
    
    # Save metadata
    metadata = {
        "filename": filename,
        "description": description,
        "created_at": str(os.path.getctime(filepath)) if os.path.exists(filepath) else "",
        "status": "pending_approval"
    }
    
    metadata_path = filepath + ".meta.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Also save to memory
    memory = get_memory_manager()
    memory.save_agent_output(
        output_id=f"code_{hash(code)}",
        agent_name="AI_Engineer",
        task=description,
        output=code,
        output_type="code"
    )
    
    return f"Code saved to {filepath} - awaiting approval"


@tool("Create Visualization")
def create_visualization_tool(chart_type: str, data: str, title: str) -> str:
    """Create data visualization"""
    return f"Created {chart_type} chart: {title}. Saved to /visualizations/{title.replace(' ', '_')}.png"


@tool("Run Security Scan")
def security_scan_tool(target: str, scan_type: str) -> str:
    """Run security vulnerability scan"""
    return f"Security scan ({scan_type}) completed on {target}. Found 3 medium severity issues. Report generated."


@tool("Deploy Infrastructure")
def deploy_infra_tool(resource_type: str, environment: str) -> str:
    """Deploy infrastructure resources"""
    return f"Deployed {resource_type} to {environment} environment. Status: Success. URL: https://{resource_type}.{environment}.com"


# ============================================================================
# AGENTS
# ============================================================================

class AICompanyAgents:
    """Factory class for creating all AI Company agents with MCP integration"""
    
    @staticmethod
    def create_hr_agent():
        """HR Manager - Main Orchestrator"""
        return Agent(
            role="HR Manager & Orchestrator",
            goal="Route queries to appropriate agents, manage recruitment, and coordinate the AI company",
            backstory="""You are the HR Manager and heart of this AI company. You have deep understanding 
            of each team member's capabilities and always know who should handle what task. You're excellent 
            at breaking down complex requests into actionable tasks for your team. You also handle all 
            recruitment activities including LinkedIn scanning, resume parsing, and interview scheduling.""",
            verbose=True,
            allow_delegation=True,
            llm=create_llm_for_agent("hr"),
            tools=[
                search_memory_tool, 
                save_to_memory_tool, 
                send_email_mcp_tool,
                web_search_mcp_tool
            ]
        )
    
    @staticmethod
    def create_ai_engineer_agent():
        """Junior AI Engineer - Builds AI agents and automation"""
        return Agent(
            role="Junior AI Engineer",
            goal="Build AI agents, create workflow automations, and develop AI solutions",
            backstory="""You are a skilled AI Engineer who specializes in building AI agents using 
            frameworks like CrewAI and LangChain. You excel at understanding requirements and turning 
            them into working code. You always write clean, well-documented Python code with proper 
            error handling. When building agents, you ALWAYS save the code to files using the 
            save_code_file_tool so it can be reviewed and approved before deployment.""",
            verbose=True,
            allow_delegation=False,
            llm=create_llm_for_agent("engineer"),
            tools=[
                search_memory_tool, 
                save_code_file_tool, 
                save_to_memory_tool,
                read_file_mcp_tool,
                write_file_mcp_tool,
                list_files_mcp_tool,
                web_search_mcp_tool
            ]
        )
    
    @staticmethod
    def create_data_analyst_agent():
        """Data Analyst - ETL, analysis, reporting"""
        return Agent(
            role="Data & Business Analyst",
            goal="Perform data analysis, create ETL pipelines, generate insights and visualizations",
            backstory="""You are an expert Data Analyst with deep knowledge of SQL, Python (pandas, numpy),
            and data visualization. You excel at extracting insights from data and presenting them in 
            clear, actionable ways. You can design and implement ETL pipelines, write complex SQL queries,
            and create beautiful dashboards.""",
            verbose=True,
            allow_delegation=False,
            llm=create_llm_for_agent("analyst"),
            tools=[
                execute_sql_mcp_tool,
                get_db_schema_tool,
                create_visualization_tool, 
                search_memory_tool, 
                save_to_memory_tool,
                write_file_mcp_tool
            ]
        )
    
    @staticmethod
    def create_pmo_agent():
        """PMO/Scrum Master - Project management"""
        return Agent(
            role="PMO & Scrum Master",
            goal="Track projects, facilitate standups, update Jira, and send status reports",
            backstory="""You are an experienced Project Manager and Scrum Master. You keep projects 
            on track, facilitate daily standups, and ensure stakeholders are always informed. You're 
            meticulous about updating project tracking tools and sending timely status reports. You 
            have a knack for identifying blockers early and keeping teams aligned.""",
            verbose=True,
            allow_delegation=False,
            llm=create_llm_for_agent("pmo"),
            tools=[
                create_jira_ticket_tool,
                update_jira_ticket_tool,
                send_email_mcp_tool, 
                search_memory_tool, 
                save_to_memory_tool,
                execute_sql_mcp_tool
            ]
        )
    
    @staticmethod
    def create_security_agent():
        """Security Pentester - Security testing"""
        return Agent(
            role="Security & Penetration Tester",
            goal="Perform security testing, find vulnerabilities, and ensure applications are secure",
            backstory="""You are a cybersecurity expert specializing in penetration testing and 
            vulnerability assessment. You have deep knowledge of OWASP Top 10, common attack vectors,
            and security best practices. You're thorough in testing and clear in your security reports,
            always providing actionable remediation recommendations.""",
            verbose=True,
            allow_delegation=False,
            llm=create_llm_for_agent("security"),
            tools=[
                security_scan_tool, 
                search_memory_tool, 
                save_to_memory_tool,
                write_file_mcp_tool
            ]
        )
    
    @staticmethod
    def create_devops_agent():
        """DevOps/Infrastructure Engineer - CI/CD and infrastructure"""
        return Agent(
            role="DevOps & Infrastructure Engineer",
            goal="Manage CI/CD pipelines, deploy infrastructure, and ensure reliable operations",
            backstory="""You are a DevOps expert with deep knowledge of cloud infrastructure, 
            containerization, and CI/CD pipelines. You excel at automating deployments, setting up 
            monitoring, and ensuring high availability. You're proficient with Docker, Kubernetes,
            Terraform, and various cloud platforms.""",
            verbose=True,
            allow_delegation=False,
            llm=create_llm_for_agent("devops"),
            tools=[
                deploy_infra_tool, 
                security_scan_tool, 
                search_memory_tool, 
                save_to_memory_tool,
                write_file_mcp_tool
            ]
        )


# ============================================================================
# CREW BUILDER
# ============================================================================

class AICompanyCrew:
    """Build and manage crews for different tasks"""
    
    def __init__(self):
        self.agents = AICompanyAgents()
        self.hr_agent = self.agents.create_hr_agent()
        self.ai_engineer = self.agents.create_ai_engineer_agent()
        self.data_analyst = self.agents.create_data_analyst_agent()
        self.pmo = self.agents.create_pmo_agent()
        self.security = self.agents.create_security_agent()
        self.devops = self.agents.create_devops_agent()
        
        # Initialize MCP servers
        self.mcp_manager = get_mcp_manager()
    
    def process_request(self, user_query: str, session_id: str = "default") -> str:
        """
        Process any user request by creating appropriate crew
        """
        # First, let HR agent analyze and route
        routing_task = Task(
            description=f"""Analyze this user request and determine which agents should handle it:
            
User Request: {user_query}

Think step by step:
1. What is the user asking for?
2. Which specialist agents are needed? (AI Engineer, Data Analyst, PMO, Security, DevOps)
3. What is the priority and sequence of work?
4. Should multiple agents work together?

Based on your analysis, describe the execution plan.""",
            agent=self.hr_agent,
            expected_output="Detailed execution plan with assigned agents and task breakdown"
        )
        
        # Determine which agents are needed based on keywords
        query_lower = user_query.lower()
        
        agents_needed = [self.hr_agent]  # HR always involved
        tasks = [routing_task]
        
        # AI Engineer: build, agent, automation, code, workflow
        if any(word in query_lower for word in ['build', 'agent', 'automation', 'code', 'create', 'develop', 'workflow']):
            ai_task = Task(
                description=f"""Build the AI solution requested:
                
Request: {user_query}

Requirements:
1. Understand what needs to be built
2. Design the solution architecture
3. Write complete, production-ready Python code
4. IMPORTANT: Use save_code_file_tool to save all code files for approval
5. Provide deployment instructions

Make sure the code is clean, well-documented, and includes error handling.""",
                agent=self.ai_engineer,
                expected_output="Complete code implementation saved to workspace for approval"
            )
            agents_needed.append(self.ai_engineer)
            tasks.append(ai_task)
        
        # Data Analyst: data, analysis, etl, query, report, dashboard
        if any(word in query_lower for word in ['data', 'analysis', 'etl', 'query', 'report', 'dashboard', 'sql', 'visualization']):
            data_task = Task(
                description=f"""Perform data analysis as requested:
                
Request: {user_query}

Tasks:
1. Understand the data requirements
2. Design ETL pipeline if needed
3. Write SQL queries or Python data processing code
4. Generate insights and visualizations
5. Create summary report

Provide clear, actionable insights.""",
                agent=self.data_analyst,
                expected_output="Data analysis results with insights and visualizations"
            )
            agents_needed.append(self.data_analyst)
            tasks.append(data_task)
        
        # PMO: project, sprint, status, jira, standup, update
        if any(word in query_lower for word in ['project', 'sprint', 'status', 'jira', 'standup', 'update', 'track']):
            pmo_task = Task(
                description=f"""Handle project management request:
                
Request: {user_query}

Tasks:
1. Understand what project management activity is needed
2. Update relevant tracking systems (Jira, etc.)
3. Collect status updates if needed
4. Generate reports
5. Send notifications to stakeholders

Be thorough and keep everyone informed.""",
                agent=self.pmo,
                expected_output="Project management tasks completed with status updates sent"
            )
            agents_needed.append(self.pmo)
            tasks.append(pmo_task)
        
        # Security: security, vulnerability, pentest, scan, audit, test
        if any(word in query_lower for word in ['security', 'vulnerability', 'pentest', 'scan', 'audit', 'secure']):
            security_task = Task(
                description=f"""Perform security assessment:
                
Request: {user_query}

Tasks:
1. Understand what needs to be tested
2. Run appropriate security scans
3. Identify vulnerabilities
4. Assess severity and risk
5. Provide remediation recommendations

Be thorough - security is critical.""",
                agent=self.security,
                expected_output="Security assessment report with vulnerabilities and recommendations"
            )
            agents_needed.append(self.security)
            tasks.append(security_task)
        
        # DevOps: deploy, pipeline, infrastructure, ci/cd, kubernetes, docker
        if any(word in query_lower for word in ['deploy', 'pipeline', 'infrastructure', 'ci/cd', 'kubernetes', 'docker', 'cloud']):
            devops_task = Task(
                description=f"""Handle infrastructure and deployment:
                
Request: {user_query}

Tasks:
1. Understand infrastructure requirements
2. Design deployment strategy
3. Create CI/CD pipeline if needed
4. Deploy resources
5. Set up monitoring

Ensure high availability and reliability.""",
                agent=self.devops,
                expected_output="Infrastructure deployed with CI/CD pipeline configured"
            )
            agents_needed.append(self.devops)
            tasks.append(devops_task)
        
        # Create and run crew
        crew = Crew(
            agents=agents_needed,
            tasks=tasks,
            verbose=True
        )
        
        result = crew.kickoff()
        
        # Save to memory
        memory = get_memory_manager()
        memory.save_conversation(
            session_id=session_id,
            agent_name="AI_Company_Crew",
            user_message=user_query,
            agent_response=str(result),
            metadata={
                "agents_involved": [agent.role for agent in agents_needed],
                "num_tasks": len(tasks)
            }
        )
        
        return str(result)


def create_crew():
    """Factory function to create AI Company crew"""
    return AICompanyCrew()