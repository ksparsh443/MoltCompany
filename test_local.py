"""
Local Test Script - Test AI Company Agents Locally
Run this to test all agents without starting the API server
"""
import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
import json

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.agents import create_crew
from src.memory_manager import get_memory_manager

# Initialize rich console for beautiful output
console = Console()

# Load environment
load_dotenv()


def check_environment():
    """Check if environment is properly configured"""
    console.print("\n[bold cyan]🔍 Checking Environment...[/bold cyan]")
    
    hf_token = os.getenv("HUGGINGFACE_API_KEY")
    
    if not hf_token or hf_token == "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
        console.print("\n[bold red]❌ HUGGINGFACE_API_KEY not configured![/bold red]")
        console.print("\n[yellow]Please follow these steps:[/yellow]")
        console.print("1. Go to https://huggingface.co/settings/tokens")
        console.print("2. Create a new token (read access is enough)")
        console.print("3. Copy the token")
        console.print("4. Create a .env file in this directory")
        console.print("5. Add: HUGGINGFACE_API_KEY=your_token_here")
        console.print("\nExample .env file:")
        console.print("[dim]HUGGINGFACE_API_KEY=hf_AbCdEfGhIjKlMnOpQrStUvWxYz[/dim]")
        return False
    
    console.print("[green]✅ Hugging Face API key found[/green]")
    console.print(f"[dim]Model: {os.getenv('HF_MODEL_NAME', 'mistralai/Mistral-7B-Instruct-v0.2')}[/dim]")
    
    return True


def print_header():
    """Print welcome header"""
    header_text = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🏢 AI COMPANY - LOCAL TEST ENVIRONMENT                ║
║        Multi-Agent System with CrewAI + Hugging Face        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Available Agents:
  👔 HR Manager - Routes queries and manages recruitment
  🛠️  AI Engineer - Builds AI agents and automation
  📊 Data Analyst - ETL, analysis, and reporting
  📋 PMO/Scrum - Project tracking and standups
  🔒 Security - Penetration testing and security
  🚀 DevOps - Infrastructure and CI/CD
"""
    console.print(Panel(header_text, style="bold cyan"))


def run_test_scenario(scenario_name: str, query: str, crew):
    """Run a test scenario"""
    console.print(f"\n{'='*70}")
    console.print(f"[bold yellow]📋 SCENARIO: {scenario_name}[/bold yellow]")
    console.print(f"{'='*70}")
    console.print(f"\n[cyan]Query:[/cyan] {query}\n")
    
    console.print("[dim]Processing... (This may take 30-60 seconds with free models)[/dim]\n")
    
    try:
        result = crew.process_request(
            user_query=query,
            session_id=f"test_{scenario_name.lower().replace(' ', '_')}"
        )
        
        console.print(Panel(
            Markdown(result),
            title="[bold green]✅ Result[/bold green]",
            border_style="green"
        ))
        
        return result
        
    except Exception as e:
        console.print(f"[bold red]❌ Error: {str(e)}[/bold red]")
        return None


def check_pending_code():
    """Check for code files pending approval"""
    pending_dir = os.getenv("AGENT_CODE_PENDING", "./agent_workspace/pending_approval")
    
    if not os.path.exists(pending_dir):
        return []
    
    files = []
    for filename in os.listdir(pending_dir):
        if filename.endswith('.meta.json'):
            continue
        
        filepath = os.path.join(pending_dir, filename)
        meta_path = filepath + ".meta.json"
        
        metadata = {}
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                metadata = json.load(f)
        
        with open(filepath, 'r') as f:
            code = f.read()
        
        files.append({
            "filename": filename,
            "filepath": filepath,
            "description": metadata.get("description", "No description"),
            "code": code
        })
    
    return files


def approve_code_interactive():
    """Interactive code approval process"""
    pending_files = check_pending_code()
    
    if not pending_files:
        console.print("\n[yellow]No code files pending approval[/yellow]")
        return
    
    console.print(f"\n[bold cyan]📁 Found {len(pending_files)} file(s) pending approval[/bold cyan]\n")
    
    for file_info in pending_files:
        console.print(f"\n{'='*70}")
        console.print(f"[bold]File:[/bold] {file_info['filename']}")
        console.print(f"[bold]Description:[/bold] {file_info['description']}")
        console.print(f"{'='*70}\n")
        
        # Show code with syntax highlighting
        from rich.syntax import Syntax
        syntax = Syntax(file_info['code'], "python", theme="monokai", line_numbers=True)
        console.print(syntax)
        
        # Ask for approval
        approved = Confirm.ask(f"\n[bold]Approve this code?[/bold]")
        
        if approved:
            # Move to approved directory
            approved_dir = os.getenv("AGENT_CODE_APPROVED", "./agent_workspace/approved")
            os.makedirs(approved_dir, exist_ok=True)
            
            approved_path = os.path.join(approved_dir, file_info['filename'])
            
            os.rename(file_info['filepath'], approved_path)
            
            # Remove metadata
            meta_path = file_info['filepath'] + ".meta.json"
            if os.path.exists(meta_path):
                os.remove(meta_path)
            
            console.print(f"[green]✅ Code approved and saved to: {approved_path}[/green]")
        else:
            # Delete file
            os.remove(file_info['filepath'])
            meta_path = file_info['filepath'] + ".meta.json"
            if os.path.exists(meta_path):
                os.remove(meta_path)
            
            console.print("[red]❌ Code rejected and deleted[/red]")


def interactive_mode(crew):
    """Interactive chat mode"""
    console.print("\n[bold cyan]💬 INTERACTIVE MODE[/bold cyan]")
    console.print("Type your queries and press Enter. Type 'exit', 'quit', or 'q' to stop.\n")
    
    session_id = f"interactive_{os.getpid()}"
    
    while True:
        try:
            query = Prompt.ask("[bold green]You[/bold green]")
            
            if not query.strip():
                continue
            
            if query.lower() in ['exit', 'quit', 'q']:
                console.print("\n[yellow]👋 Goodbye![/yellow]")
                break
            
            # Check for special commands
            if query.lower() == 'approve code':
                approve_code_interactive()
                continue
            
            if query.lower() == 'check code':
                pending_files = check_pending_code()
                if pending_files:
                    console.print(f"\n[cyan]{len(pending_files)} file(s) pending approval:[/cyan]")
                    for f in pending_files:
                        console.print(f"  - {f['filename']}: {f['description']}")
                else:
                    console.print("\n[yellow]No pending code files[/yellow]")
                continue
            
            # Process query
            console.print("\n[dim]Processing...[/dim]\n")
            
            result = crew.process_request(
                user_query=query,
                session_id=session_id
            )
            
            console.print(Panel(
                Markdown(result),
                title="[bold cyan]🤖 AI Company[/bold cyan]",
                border_style="cyan"
            ))
            
            # Check if code was generated
            pending_files = check_pending_code()
            if pending_files:
                console.print(f"\n[yellow]💡 Tip: {len(pending_files)} code file(s) generated. Type 'approve code' to review.[/yellow]")
            
        except KeyboardInterrupt:
            console.print("\n\n[yellow]👋 Interrupted. Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {str(e)}[/red]\n")


def run_all_test_scenarios(crew):
    """Run all predefined test scenarios"""
    scenarios = [
        {
            "name": "HR - Interview Scheduling",
            "query": "Schedule interviews for 3 senior AI engineers next week. Find candidates on LinkedIn with 5+ years experience in Python and ML."
        },
        {
            "name": "AI Engineer - Build Agent",
            "query": "Build me a customer support AI agent that can answer questions from a knowledge base and create support tickets in Jira when needed."
        },
        {
            "name": "Data Analyst - Analytics",
            "query": "Analyze our sales data from the last quarter. Create visualizations showing trends by region and product category."
        },
        {
            "name": "PMO - Daily Standup",
            "query": "It's time for daily standup. Collect status updates from all team members and send a summary to stakeholders."
        },
        {
            "name": "Security - Pentest",
            "query": "Run a security scan on our web application. Check for OWASP Top 10 vulnerabilities and provide a report."
        },
        {
            "name": "DevOps - Deployment",
            "query": "Deploy the new microservice to production with a CI/CD pipeline. Include SonarQube scanning and monitoring setup."
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        if i > 1:
            if not Confirm.ask(f"\n[bold]Run next scenario ({i}/{len(scenarios)})?[/bold]"):
                break
        
        run_test_scenario(scenario["name"], scenario["query"], crew)
    
    # Check for generated code at the end
    console.print("\n" + "="*70)
    pending_files = check_pending_code()
    if pending_files:
        console.print(f"\n[bold yellow]📁 {len(pending_files)} code file(s) generated during testing[/bold yellow]")
        if Confirm.ask("[bold]Review and approve code now?[/bold]"):
            approve_code_interactive()


def main():
    """Main test function"""
    print_header()
    
    # Check environment
    if not check_environment():
        return
    
    console.print("\n[bold cyan]🚀 Initializing AI Company...[/bold cyan]")
    
    try:
        # Initialize crew
        crew = create_crew()
        memory = get_memory_manager()
        
        console.print("[green]✅ AI Company initialized successfully![/green]\n")
        
        # Show menu
        console.print("[bold]Choose an option:[/bold]")
        console.print("  1. Run all test scenarios (automated)")
        console.print("  2. Interactive mode (chat with AI company)")
        console.print("  3. Approve pending code files")
        console.print("  4. Quick single test")
        
        choice = Prompt.ask("\nYour choice", choices=["1", "2", "3", "4"], default="2")
        
        if choice == "1":
            run_all_test_scenarios(crew)
        elif choice == "2":
            interactive_mode(crew)
        elif choice == "3":
            approve_code_interactive()
        elif choice == "4":
            query = Prompt.ask("\n[bold]Enter your test query[/bold]")
            run_test_scenario("Quick Test", query, crew)
        
        console.print("\n[bold green]✅ Testing complete![/bold green]")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]")
        import traceback
        console.print(f"\n[dim]{traceback.format_exc()}[/dim]")


if __name__ == "__main__":
    main()
