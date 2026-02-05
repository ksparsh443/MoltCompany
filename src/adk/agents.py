"""
AI Company Agents - Google ADK Implementation

Multi-agent system with 6 specialist agents using ADK's LlmAgent.
HR Manager acts as the root coordinator with sub_agents for delegation.
"""

import os
import logging
from typing import Optional, List, Any

from google.adk.agents import LlmAgent

from src.adk.models import get_model
from src.adk.tools import (
    HR_TOOLS,
    ENGINEER_TOOLS,
    ANALYST_TOOLS,
    PMO_TOOLS,
    SECURITY_TOOLS,
    DEVOPS_TOOLS,
)

logger = logging.getLogger(__name__)


# ============================================================================
# AGENT INSTRUCTIONS
# ============================================================================

HR_INSTRUCTION = """You are the HR Manager and Orchestrator of this AI company. You have deep understanding
of each team member's capabilities and always know who should handle what task.

Your responsibilities:
1. Analyze incoming requests and determine which specialist agent should handle them
2. Break down complex requests into actionable tasks for your team
3. Manage recruitment activities including resume scanning and interview scheduling
4. Coordinate multi-agent workflows when multiple specialists are needed
5. Maintain professional communication with users

When routing tasks:
- AI/Code/Automation tasks → AI Engineer
- Data/Analysis/SQL/Reports → Data Analyst
- Project/Sprint/Jira/Standup → PMO/Scrum Master
- Security/Vulnerability/Pentest → Security Pentester
- Deploy/Infrastructure/CI-CD → DevOps Engineer

For complex tasks requiring multiple specialists, delegate to each in sequence and coordinate their work.
Always provide a clear summary of what was accomplished and by whom."""

AI_ENGINEER_INSTRUCTION = """You are a skilled Junior AI Engineer who specializes in building AI agents and
workflow automations. You excel at understanding requirements and turning them into working code.

Your responsibilities:
1. Build AI agents using modern frameworks
2. Create workflow automations
3. Write clean, well-documented Python code with proper error handling
4. Generate production-ready solutions

IMPORTANT: When building agents or creating code:
1. Always use the save_code_file tool to save generated code for review
2. Include comprehensive docstrings and comments
3. Add error handling and logging
4. Consider security implications
5. Provide deployment instructions

Your code should be:
- Clean and readable
- Well-documented
- Properly tested
- Production-ready"""

DATA_ANALYST_INSTRUCTION = """You are an expert Data Analyst with deep knowledge of SQL, Python (pandas, numpy),
and data visualization. You excel at extracting insights from data and presenting them clearly.

Your responsibilities:
1. Design and implement ETL pipelines
2. Write complex SQL queries for data extraction
3. Perform data analysis and generate insights
4. Create visualizations (charts, dashboards)
5. Generate reports with actionable recommendations

When analyzing data:
1. First understand the data schema using get_database_schema
2. Write efficient SQL queries
3. Present findings with clear visualizations
4. Provide actionable insights
5. Save reports and code for reference"""

PMO_INSTRUCTION = """You are an experienced Project Manager and Scrum Master. You keep projects on track,
facilitate daily standups, and ensure stakeholders are always informed.

Your responsibilities:
1. Track project progress and milestones
2. Create and update Jira tickets for task management
3. Facilitate daily standups and retrospectives
4. Send status reports to stakeholders
5. Identify and escalate blockers

When managing projects:
1. Create clear, actionable Jira tickets
2. Track dependencies between tasks
3. Communicate status proactively
4. Identify risks early
5. Keep all stakeholders informed"""

SECURITY_INSTRUCTION = """You are a cybersecurity expert specializing in penetration testing and
vulnerability assessment. You have deep knowledge of OWASP Top 10 and security best practices.

Your responsibilities:
1. Perform security assessments and penetration tests
2. Identify vulnerabilities and assess risk
3. Generate comprehensive security reports
4. Provide actionable remediation recommendations
5. Review code for security issues

When conducting security assessments:
1. Use systematic testing methodology
2. Document all findings with severity levels
3. Provide clear remediation steps
4. Consider business impact
5. Follow responsible disclosure practices

IMPORTANT: Only perform security testing on authorized systems."""

DEVOPS_INSTRUCTION = """You are a DevOps expert with deep knowledge of cloud infrastructure,
containerization, and CI/CD pipelines. You ensure reliable operations and deployments.

Your responsibilities:
1. Design and implement CI/CD pipelines
2. Provision and manage infrastructure
3. Set up monitoring and alerting
4. Ensure high availability and reliability
5. Implement security best practices

When deploying infrastructure:
1. Follow infrastructure-as-code principles
2. Implement proper security controls
3. Set up comprehensive monitoring
4. Plan for scalability
5. Document deployment procedures"""


# ============================================================================
# AGENT FACTORY
# ============================================================================

class AICompanyAgents:
    """Factory class for creating ADK agents"""

    @staticmethod
    def create_ai_engineer() -> LlmAgent:
        """Create AI Engineer agent"""
        return LlmAgent(
            model=get_model(role="engineer"),
            name="AI_Engineer",
            description="Builds AI agents, creates workflow automations, and develops AI solutions. "
                       "Expert in Python, CrewAI, LangChain, and modern AI frameworks.",
            instruction=AI_ENGINEER_INSTRUCTION,
            tools=ENGINEER_TOOLS,
        )

    @staticmethod
    def create_data_analyst() -> LlmAgent:
        """Create Data Analyst agent"""
        return LlmAgent(
            model=get_model(role="analyst"),
            name="Data_Analyst",
            description="Performs data analysis, creates ETL pipelines, generates insights and visualizations. "
                       "Expert in SQL, Python, pandas, and data visualization.",
            instruction=DATA_ANALYST_INSTRUCTION,
            tools=ANALYST_TOOLS,
        )

    @staticmethod
    def create_pmo() -> LlmAgent:
        """Create PMO/Scrum Master agent"""
        return LlmAgent(
            model=get_model(role="pmo"),
            name="PMO_Scrum_Master",
            description="Manages projects, facilitates standups, updates Jira, and sends status reports. "
                       "Expert in Agile, Scrum, and project management.",
            instruction=PMO_INSTRUCTION,
            tools=PMO_TOOLS,
        )

    @staticmethod
    def create_security() -> LlmAgent:
        """Create Security Pentester agent"""
        return LlmAgent(
            model=get_model(role="security"),
            name="Security_Pentester",
            description="Performs security testing, finds vulnerabilities, and ensures applications are secure. "
                       "Expert in OWASP Top 10, penetration testing, and security audits.",
            instruction=SECURITY_INSTRUCTION,
            tools=SECURITY_TOOLS,
        )

    @staticmethod
    def create_devops() -> LlmAgent:
        """Create DevOps Engineer agent"""
        return LlmAgent(
            model=get_model(role="devops"),
            name="DevOps_Engineer",
            description="Manages CI/CD pipelines, deploys infrastructure, and ensures reliable operations. "
                       "Expert in Docker, Kubernetes, Terraform, and cloud platforms.",
            instruction=DEVOPS_INSTRUCTION,
            tools=DEVOPS_TOOLS,
        )

    @staticmethod
    def create_hr_manager(sub_agents: Optional[List[LlmAgent]] = None) -> LlmAgent:
        """
        Create HR Manager (root coordinator) agent.

        Args:
            sub_agents: List of specialist agents to delegate to.
                       If None, creates all specialists automatically.
        """
        if sub_agents is None:
            # Create all specialist agents
            sub_agents = [
                AICompanyAgents.create_ai_engineer(),
                AICompanyAgents.create_data_analyst(),
                AICompanyAgents.create_pmo(),
                AICompanyAgents.create_security(),
                AICompanyAgents.create_devops(),
            ]

        return LlmAgent(
            model=get_model(role="hr"),
            name="HR_Manager",
            description="Routes queries to appropriate specialist agents, manages recruitment, "
                       "and coordinates the AI company. Main orchestrator for all tasks.",
            instruction=HR_INSTRUCTION,
            tools=HR_TOOLS,
            sub_agents=sub_agents,
        )


def create_root_agent() -> LlmAgent:
    """
    Create the root agent (HR Manager) with all sub-agents.

    This is the main entry point for the AI Company agent system.
    The root agent automatically delegates tasks to specialist agents
    based on the request content.

    Returns:
        LlmAgent: HR Manager agent with all specialists as sub_agents
    """
    logger.info("Creating AI Company agent hierarchy...")

    # Create specialist agents
    ai_engineer = AICompanyAgents.create_ai_engineer()
    data_analyst = AICompanyAgents.create_data_analyst()
    pmo = AICompanyAgents.create_pmo()
    security = AICompanyAgents.create_security()
    devops = AICompanyAgents.create_devops()

    # Create root agent with sub_agents
    root_agent = AICompanyAgents.create_hr_manager(
        sub_agents=[ai_engineer, data_analyst, pmo, security, devops]
    )

    logger.info(f"Created agent hierarchy with {len(root_agent.sub_agents)} specialist agents")
    logger.info("Agents: HR_Manager (root) -> AI_Engineer, Data_Analyst, PMO_Scrum_Master, Security_Pentester, DevOps_Engineer")

    return root_agent


def get_agent_info() -> dict:
    """Get information about all agents"""
    return {
        "root_agent": {
            "name": "HR_Manager",
            "role": "Orchestrator & Human Resources",
            "capabilities": [
                "Route queries to appropriate agents",
                "Recruit and hire employees",
                "Schedule interviews",
                "Coordinate multi-agent workflows"
            ]
        },
        "sub_agents": [
            {
                "name": "AI_Engineer",
                "role": "AI Development & Automation",
                "capabilities": [
                    "Build AI agents",
                    "Create workflow automations",
                    "Generate Python code",
                    "Implement AI solutions"
                ]
            },
            {
                "name": "Data_Analyst",
                "role": "Data Analysis & Business Intelligence",
                "capabilities": [
                    "ETL pipeline design",
                    "SQL query optimization",
                    "Data visualization",
                    "Business insights and reporting"
                ]
            },
            {
                "name": "PMO_Scrum_Master",
                "role": "Project Management",
                "capabilities": [
                    "Project tracking (Jira)",
                    "Daily standups",
                    "Sprint planning",
                    "Status reporting"
                ]
            },
            {
                "name": "Security_Pentester",
                "role": "Security Testing",
                "capabilities": [
                    "Penetration testing",
                    "Vulnerability scanning",
                    "Security audits",
                    "OWASP Top 10 assessment"
                ]
            },
            {
                "name": "DevOps_Engineer",
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
# TEST
# ============================================================================

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("Testing AI Company Agents...")
    print("=" * 50)

    try:
        # Create root agent
        root_agent = create_root_agent()
        print(f"✅ Root agent created: {root_agent.name}")
        print(f"   Model: {root_agent.model}")
        print(f"   Sub-agents: {len(root_agent.sub_agents)}")

        for agent in root_agent.sub_agents:
            print(f"     - {agent.name}: {agent.description[:50]}...")

        # Get agent info
        info = get_agent_info()
        print(f"\n✅ Agent info retrieved")
        print(f"   Root: {info['root_agent']['name']}")
        print(f"   Sub-agents: {len(info['sub_agents'])}")

        print("\n✅ All agents created successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
