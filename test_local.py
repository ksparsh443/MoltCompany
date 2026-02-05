"""
Local Test Script - Test AI Company Agents Locally (Google ADK Edition)
Run this to test all agents without starting the API server
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
import json

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

# Set PYTHONUTF8 for Windows compatibility
os.environ["PYTHONUTF8"] = "1"

# Load environment
load_dotenv()

# Initialize rich console for beautiful output
console = Console()


def check_environment():
    """Check if environment is properly configured"""
    console.print("\n[bold cyan]🔍 Checking Environment...[/bold cyan]")

    model_provider = os.getenv("MODEL_PROVIDER", "gemini")
    console.print(f"[dim]Model Provider: {model_provider}[/dim]")

    if model_provider == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            console.print("\n[bold red]❌ GOOGLE_API_KEY not configured![/bold red]")
            console.print("\n[yellow]Please follow these steps:[/yellow]")
            console.print("1. Go to https://aistudio.google.com/apikey")
            console.print("2. Create a new API key")
            console.print("3. Copy the key")
            console.print("4. Add to .env file: GOOGLE_API_KEY=your_key_here")
            return False
        console.print("[green]✅ Gemini API key found[/green]")
        console.print(f"[dim]Model: {os.getenv('GEMINI_MODEL_NAME', 'gemini-2.0-flash')}[/dim]")

    elif model_provider == "huggingface":
        hf_token = os.getenv("HUGGINGFACE_API_KEY")
        if not hf_token or hf_token.startswith("hf_xxx"):
            console.print("\n[bold red]❌ HUGGINGFACE_API_KEY not configured![/bold red]")
            console.print("\n[yellow]Please follow these steps:[/yellow]")
            console.print("1. Go to https://huggingface.co/settings/tokens")
            console.print("2. Create a new token (read access is enough)")
            console.print("3. Copy the token")
            console.print("4. Add to .env file: HUGGINGFACE_API_KEY=hf_your_token_here")
            return False
        console.print("[green]✅ Hugging Face API key found[/green]")
        console.print(f"[dim]Model: {os.getenv('HF_MODEL_NAME', 'mistralai/Mistral-7B-Instruct-v0.2')}[/dim]")

    elif model_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            console.print("\n[bold red]❌ OPENAI_API_KEY not configured![/bold red]")
            return False
        console.print("[green]✅ OpenAI API key found[/green]")

    return True


def print_header():
    """Print welcome header"""
    header_text = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🏢 AI COMPANY - LOCAL TEST ENVIRONMENT                ║
║        Multi-Agent System with Google ADK                    ║
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


async def run_test_scenario(scenario_name: str, query: str, runner):
    """Run a test scenario"""
    console.print(f"\n{'='*70}")
    console.print(f"[bold yellow]📋 SCENARIO: {scenario_name}[/bold yellow]")
    console.print(f"{'='*70}")
    console.print(f"\n[cyan]Query:[/cyan] {query}\n")

    console.print("[dim]Processing... (This may take a moment)[/dim]\n")

    try:
        result = await runner.process_request(
            query=query,
            session_id=f"test_{scenario_name.lower().replace(' ', '_')}"
        )

        if result["status"] == "success":
            console.print(Panel(
                Markdown(result["result"]),
                title="[bold green]✅ Result[/bold green]",
                border_style="green"
            ))
        else:
            console.print(f"[bold red]❌ Error: {result.get('error', 'Unknown error')}[/bold red]")

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


async def interactive_mode(runner):
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

            if query.lower() == 'stats':
                stats = runner.get_stats()
                console.print("\n[bold cyan]📊 System Stats:[/bold cyan]")
                console.print(json.dumps(stats, indent=2))
                continue

            if query.lower() == 'agents':
                info = runner.get_agents_info()
                console.print("\n[bold cyan]🤖 Available Agents:[/bold cyan]")
                console.print(f"Root: {info['root_agent']['name']}")
                for agent in info['sub_agents']:
                    console.print(f"  - {agent['name']}: {agent['role']}")
                continue

            if query.lower() == 'help':
                console.print("\n[bold cyan]📖 Available Commands:[/bold cyan]")
                console.print("  approve code - Review and approve pending code files")
                console.print("  check code   - List pending code files")
                console.print("  stats        - Show system statistics")
                console.print("  agents       - List available agents")
                console.print("  help         - Show this help message")
                console.print("  exit/quit/q  - Exit interactive mode")
                continue

            # Process query
            console.print("\n[dim]Processing...[/dim]\n")

            result = await runner.process_request(
                query=query,
                session_id=session_id
            )

            if result["status"] == "success":
                console.print(Panel(
                    Markdown(result["result"]),
                    title="[bold cyan]🤖 AI Company[/bold cyan]",
                    border_style="cyan"
                ))
            else:
                console.print(f"[bold red]❌ Error: {result.get('error', 'Unknown error')}[/bold red]")

            # Check if code was generated
            pending_files = check_pending_code()
            if pending_files:
                console.print(f"\n[yellow]💡 Tip: {len(pending_files)} code file(s) generated. Type 'approve code' to review.[/yellow]")

        except KeyboardInterrupt:
            console.print("\n\n[yellow]👋 Interrupted. Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {str(e)}[/red]\n")


async def run_all_test_scenarios(runner):
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

        await run_test_scenario(scenario["name"], scenario["query"], runner)

    # Check for generated code at the end
    console.print("\n" + "="*70)
    pending_files = check_pending_code()
    if pending_files:
        console.print(f"\n[bold yellow]📁 {len(pending_files)} code file(s) generated during testing[/bold yellow]")
        if Confirm.ask("[bold]Review and approve code now?[/bold]"):
            approve_code_interactive()


async def main_async():
    """Async main function"""
    print_header()

    # Check environment
    if not check_environment():
        return

    console.print("\n[bold cyan]🚀 Initializing AI Company (Google ADK)...[/bold cyan]")

    try:
        # Initialize runner
        from src.adk.runner import create_runner
        from src.adk.memory import get_memory_service

        runner = create_runner()
        memory = get_memory_service()

        console.print("[green]✅ AI Company initialized successfully![/green]")
        console.print(f"[dim]Root Agent: {runner.root_agent.name}[/dim]")
        console.print(f"[dim]Sub-agents: {len(runner.root_agent.sub_agents)}[/dim]\n")

        # Show menu
        console.print("[bold]Choose an option:[/bold]")
        console.print("  1. Run all test scenarios (automated)")
        console.print("  2. Interactive mode (chat with AI company)")
        console.print("  3. Approve pending code files")
        console.print("  4. Quick single test")
        console.print("  5. Show system stats")

        choice = Prompt.ask("\nYour choice", choices=["1", "2", "3", "4", "5"], default="2")

        if choice == "1":
            await run_all_test_scenarios(runner)
        elif choice == "2":
            await interactive_mode(runner)
        elif choice == "3":
            approve_code_interactive()
        elif choice == "4":
            query = Prompt.ask("\n[bold]Enter your test query[/bold]")
            await run_test_scenario("Quick Test", query, runner)
        elif choice == "5":
            stats = runner.get_stats()
            console.print("\n[bold cyan]📊 System Stats:[/bold cyan]")
            console.print(json.dumps(stats, indent=2))

        console.print("\n[bold green]✅ Testing complete![/bold green]")

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]")
        import traceback
        console.print(f"\n[dim]{traceback.format_exc()}[/dim]")


def main():
    """Main entry point"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
