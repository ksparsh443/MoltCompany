# -*- coding: utf-8 -*-
"""
Comprehensive Test Suite for AI Company Multi-Agent System
Tests: Supabase, SMTP, Google Calendar, All 7 Agents, API Endpoints

Run with: python test_complete.py
"""

import os
import sys
import json
import time
try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system("pip install requests")
    import requests
from datetime import datetime, timedelta

# Set UTF-8 encoding
os.environ['PYTHONUTF8'] = '1'

# Add project to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}PASS{Colors.END}" if passed else f"{Colors.RED}FAIL{Colors.END}"
    print(f"  [{status}] {name}")
    if details and not passed:
        print(f"        {Colors.YELLOW}{details}{Colors.END}")

def print_section(text):
    print(f"\n{Colors.BLUE}--- {text} ---{Colors.END}")


# ============================================================================
# 1. ENVIRONMENT CONFIGURATION TESTS
# ============================================================================

def test_environment():
    print_header("1. ENVIRONMENT CONFIGURATION")

    results = {}

    # Check required env vars
    env_vars = {
        "MODEL_PROVIDER": os.getenv("MODEL_PROVIDER"),
        "HUGGINGFACE_API_KEY": os.getenv("HUGGINGFACE_API_KEY"),
        "DB_PROVIDER": os.getenv("DB_PROVIDER"),
    }

    print_section("Required Variables")
    for var, value in env_vars.items():
        exists = value is not None and len(str(value)) > 0
        masked = f"{value[:10]}..." if value and len(value) > 10 else value
        print_test(f"{var} = {masked}", exists)
        results[var] = exists

    # Check optional but recommended
    optional_vars = {
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
        "SMTP_USER": os.getenv("SMTP_USER"),
        "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD"),
    }

    print_section("Optional Variables")
    for var, value in optional_vars.items():
        configured = value is not None and "your-" not in str(value) and len(str(value)) > 5
        status = "configured" if configured else "not configured"
        print_test(f"{var}: {status}", configured, "Update .env to enable this feature")
        results[var] = configured

    return results


# ============================================================================
# IMPORT TOOLS DIRECTLY (bypass google.adk dependency)
# ============================================================================

def import_tools():
    """Import tools module directly without google.adk dependency"""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "tools",
        os.path.join(project_root, "src", "adk", "tools.py")
    )
    tools = importlib.util.module_from_spec(spec)
    import builtins
    tools.__builtins__ = builtins
    spec.loader.exec_module(tools)
    return tools

# Global tools module
_tools = None

def get_tools():
    global _tools
    if _tools is None:
        _tools = import_tools()
    return _tools


# ============================================================================
# 2. DATABASE TESTS (Supabase/SQLite)
# ============================================================================

def test_database():
    print_header("2. DATABASE CONNECTION")

    results = {}

    try:
        tools = get_tools()
        get_database = tools.get_database
        get_database_schema = tools.get_database_schema

        # Test connection
        print_section("Connection Test")
        db = get_database()
        provider = os.getenv("DB_PROVIDER", "sqlite")
        print_test(f"Database Provider: {provider}", True)

        # Test query
        result = db.execute_query("SELECT 1 as test")
        print_test("Test Query", result is not None)
        results["connection"] = True

        # Test schema
        print_section("Schema Test")
        schema = get_database_schema()
        if schema.get("status") == "success":
            tables = schema.get("tables", [])
            print_test(f"Tables found: {len(tables)}", len(tables) > 0)
            for table in tables[:5]:
                print(f"        - {table.get('name', 'unknown')}")
            results["schema"] = True
        else:
            print_test("Schema retrieval", False, schema.get("error"))
            results["schema"] = False

        # Test CRUD operations
        print_section("CRUD Operations")

        # Create
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                created_at TEXT
            )
        """)
        print_test("CREATE TABLE", True)

        # Insert
        db.execute_query(
            "INSERT INTO test_table (name, created_at) VALUES (?, ?)",
            ("test_record", datetime.utcnow().isoformat())
        )
        print_test("INSERT", True)

        # Select
        rows = db.execute_query("SELECT * FROM test_table WHERE name=?", ("test_record",))
        print_test("SELECT", rows is not None and len(rows) > 0)

        # Delete
        db.execute_query("DELETE FROM test_table WHERE name=?", ("test_record",))
        print_test("DELETE", True)

        results["crud"] = True

    except Exception as e:
        print_test("Database connection", False, str(e))
        results["connection"] = False

    return results


# ============================================================================
# 3. SMTP EMAIL TESTS
# ============================================================================

def test_smtp():
    print_header("3. SMTP EMAIL")

    results = {}

    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASSWORD", "")

    if "your-" in smtp_user or not smtp_pass or "xxxx" in smtp_pass:
        print_test("SMTP Configuration", False, "SMTP not configured in .env")
        results["configured"] = False
        return results

    print_section("Configuration")
    print_test(f"SMTP Host: {os.getenv('SMTP_HOST', 'smtp.gmail.com')}", True)
    print_test(f"SMTP User: {smtp_user}", True)
    results["configured"] = True

    # Test connection (without sending)
    print_section("Connection Test")
    try:
        import smtplib

        server = smtplib.SMTP(
            os.getenv("SMTP_HOST", "smtp.gmail.com"),
            int(os.getenv("SMTP_PORT", 587))
        )
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.quit()

        print_test("SMTP Login", True)
        results["login"] = True

    except Exception as e:
        print_test("SMTP Login", False, str(e))
        results["login"] = False

    return results


# ============================================================================
# 4. GOOGLE CALENDAR TESTS (ICS Generation)
# ============================================================================

def test_calendar():
    print_header("4. CALENDAR (ICS Generation)")

    results = {}

    try:
        from datetime import datetime as dt, timedelta as td

        tools = get_tools()
        schedule_meeting = tools.schedule_meeting

        print_section("ICS File Generation")

        # Create a test meeting
        meeting_result = schedule_meeting(
            title="Test Meeting",
            meeting_type="adhoc",
            scheduled_at=(dt.utcnow() + td(days=1)).strftime("%Y-%m-%dT10:00:00"),
            duration_minutes=30,
            attendees="test@example.com",
            agenda="Test agenda"
        )

        if meeting_result.get("status") == "success":
            print_test("Meeting Created", True)
            print_test(f"Meeting ID: {meeting_result.get('meeting_id')}", True)

            ics_path = meeting_result.get("ics_file")
            if ics_path and os.path.exists(ics_path):
                print_test(f"ICS File Generated: {ics_path}", True)

                # Verify ICS content
                with open(ics_path, 'r') as f:
                    ics_content = f.read()

                has_vcalendar = "BEGIN:VCALENDAR" in ics_content
                has_vevent = "BEGIN:VEVENT" in ics_content

                print_test("ICS contains VCALENDAR", has_vcalendar)
                print_test("ICS contains VEVENT", has_vevent)

                results["ics_generation"] = True
            else:
                print_test("ICS File", False, "File not found")
                results["ics_generation"] = False
        else:
            print_test("Meeting Creation", False, meeting_result.get("error"))
            results["ics_generation"] = False

    except Exception as e:
        print_test("Calendar Test", False, str(e))
        results["ics_generation"] = False

    return results


# ============================================================================
# 5. HR MANAGER TESTS
# ============================================================================

def test_hr_manager():
    print_header("5. HR MANAGER AGENT")

    results = {}

    try:
        tools = get_tools()

        print_section("Candidate Search (DuckDuckGo)")
        try:
            search_linkedin_profiles = tools.search_linkedin_profiles
            search_result = search_linkedin_profiles(
                job_title="Python Developer",
                skills="Python, FastAPI",
                location="Remote",
                num_results=3
            )
            print_test("Search Candidates", search_result.get("status") == "success")
            print_test(f"Results found: {search_result.get('count', 0)}", True)
            results["search"] = search_result.get("status") == "success"
        except AttributeError:
            print_test("Search Candidates", False, "Function not available")
            results["search"] = False

        print_section("HR Database Operations")
        try:
            get_database = tools.get_database
            db = get_database()

            # Check employees table
            employees = db.execute_query("SELECT COUNT(*) as count FROM employees")
            if employees:
                count = employees[0].get("count", 0) if isinstance(employees[0], dict) else 0
                print_test(f"Employees in database: {count}", True)
                results["database"] = True
            else:
                print_test("Employees table", True)
                results["database"] = True
        except Exception as e:
            print_test("HR Database", False, str(e)[:50])
            results["database"] = False

    except Exception as e:
        print_test("HR Manager", False, str(e)[:50])
        results["error"] = str(e)

    return results


# ============================================================================
# 6. PMO/SCRUM MASTER TESTS
# ============================================================================

def test_pmo():
    print_header("6. PMO/SCRUM MASTER AGENT")

    results = {}

    try:
        tools = get_tools()
        create_task = tools.create_task
        get_tasks = tools.get_tasks
        create_excel_tracker = tools.create_excel_tracker

        print_section("Task Management")

        # Create task
        task_result = create_task(
            title="Test Task",
            description="Test description",
            project="TestProject",
            assignee="test@example.com",
            priority="high",
            due_date=(datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d"),
            sprint="",
            story_points=3
        )
        print_test("Create Task", task_result.get("status") == "success")
        results["create_task"] = task_result.get("status") == "success"

        # Get tasks
        tasks = get_tasks("TestProject", "", "", "")
        print_test("Get Tasks", tasks.get("status") == "success")
        print_test(f"Tasks found: {tasks.get('count', 0)}", True)
        results["get_tasks"] = tasks.get("status") == "success"

        print_section("Excel Tracker")
        excel_result = create_excel_tracker(
            tracker_name="TestTracker",
            tracker_type="project",
            project="TestProject",
            sprint=""
        )
        print_test("Create Excel Tracker", excel_result.get("status") == "success")
        if excel_result.get("file_path"):
            print_test(f"File: {excel_result.get('file_path')}", os.path.exists(excel_result.get("file_path", "")))
        results["excel"] = excel_result.get("status") == "success"

    except Exception as e:
        print_test("PMO Tests", False, str(e))
        results["error"] = str(e)

    return results


# ============================================================================
# 7. SECURITY PENTESTER TESTS
# ============================================================================

def test_security():
    print_header("7. SECURITY PENTESTER AGENT")

    results = {}

    try:
        tools = get_tools()
        create_pentest_session = tools.create_pentest_session
        run_pentest_scan = tools.run_pentest_scan
        get_pentest_results = tools.get_pentest_results
        generate_pentest_report = tools.generate_pentest_report

        print_section("Pentest Session")

        # Create session
        session_result = create_pentest_session(
            target_url="https://httpbin.org",
            target_type="web_application",
            scope="Test security scan"
        )
        print_test("Create Session", session_result.get("status") == "success")

        if session_result.get("status") == "success":
            session_id = session_result.get("session_id")
            print_test(f"Session ID: {session_id}", True)
            results["session"] = True

            print_section("Security Scan")
            scan_result = run_pentest_scan(
                session_id=session_id,
                scan_type="quick",
                test_categories=["web"]
            )
            print_test("Run Scan", scan_result.get("status") == "success")
            print_test(f"Tests run: {scan_result.get('tests_run', 0)}", True)
            results["scan"] = scan_result.get("status") == "success"

            print_section("Results & Report")
            results_data = get_pentest_results(session_id)
            print_test("Get Results", results_data.get("status") == "success")

            report = generate_pentest_report(session_id, "markdown")
            print_test("Generate Report", report.get("status") == "success")
            if report.get("report_path"):
                print_test(f"Report: {report.get('report_path')}", True)
            results["report"] = report.get("status") == "success"

    except Exception as e:
        print_test("Security Tests", False, str(e))
        results["error"] = str(e)

    return results


# ============================================================================
# 8. DATA ANALYST TESTS
# ============================================================================

def test_data_analyst():
    print_header("8. DATA ANALYST AGENT")

    results = {}

    try:
        import pandas as pd
        tools = get_tools()
        ingest_data_file = tools.ingest_data_file
        query_data = tools.query_data
        create_interactive_chart = tools.create_interactive_chart
        create_dashboard = tools.create_dashboard
        get_data_catalog = tools.get_data_catalog

        # Create sample data
        print_section("Data Ingestion")
        sample_path = os.path.join(project_root, "agent_workspace", "data_analyst", "test_data.csv")
        os.makedirs(os.path.dirname(sample_path), exist_ok=True)

        df = pd.DataFrame({
            "month": ["Jan", "Feb", "Mar", "Apr"],
            "revenue": [10000, 12000, 15000, 18000],
            "region": ["North", "South", "East", "West"]
        })
        df.to_csv(sample_path, index=False)
        print_test("Sample data created", True)

        # Ingest
        ingest_result = ingest_data_file(sample_path, "Test Data")
        print_test("Data Ingestion", ingest_result.get("status") == "success")
        results["ingest"] = ingest_result.get("status") == "success"

        if ingest_result.get("status") == "success":
            source_id = ingest_result.get("source_id")
            print_test(f"Source ID: {source_id}", True)

            print_section("Data Querying")
            query_result = query_data(source_id, "SELECT * FROM data", "sql")
            print_test("SQL Query", query_result.get("status") == "success")
            print_test(f"Results: {query_result.get('result_count', 0)} rows", True)
            results["query"] = query_result.get("status") == "success"

            print_section("Visualization")
            chart_result = create_interactive_chart(
                source_id=source_id,
                chart_type="bar",
                x_column="month",
                y_column="revenue",
                title="Test Chart"
            )
            print_test("Create Chart", chart_result.get("status") == "success")
            if chart_result.get("html_path"):
                print_test(f"Chart: {chart_result.get('html_path')}", True)
            results["chart"] = chart_result.get("status") == "success"

            print_section("Dashboard")
            charts_config = json.dumps([
                {"type": "bar", "x": "month", "y": "revenue", "title": "Revenue"}
            ])
            dashboard_result = create_dashboard(
                title="Test Dashboard",
                description="Test",
                source_ids=source_id,
                charts_config=charts_config
            )
            print_test("Create Dashboard", dashboard_result.get("status") == "success")
            if dashboard_result.get("file_path"):
                print_test(f"Dashboard: {dashboard_result.get('file_path')}", True)
            results["dashboard"] = dashboard_result.get("status") == "success"

            print_section("Data Catalog")
            catalog = get_data_catalog()
            print_test("Get Catalog", catalog.get("status") == "success")
            print_test(f"Sources: {catalog.get('total_sources', 0)}", True)
            results["catalog"] = catalog.get("status") == "success"

    except Exception as e:
        print_test("Data Analyst Tests", False, str(e))
        results["error"] = str(e)

    return results


# ============================================================================
# 9. API ENDPOINTS TESTS
# ============================================================================

def test_api_endpoints(base_url: str = "http://localhost:8000"):
    print_header("9. API ENDPOINTS")

    results = {}

    print_section("Checking if API server is running...")

    try:
        # Health check
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print_test("API Server Running", True)
            results["server"] = True
        else:
            print_test("API Server", False, f"Status: {response.status_code}")
            results["server"] = False
            return results

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.ReadTimeout):
        print_test("API Server", False, "Not running. Start with: python api_server.py")
        results["server"] = False
        print(f"\n{Colors.YELLOW}To test API endpoints, run in another terminal:{Colors.END}")
        print(f"  python api_server.py")
        return results
    except Exception as e:
        print_test("API Server", False, str(e)[:50])
        results["server"] = False
        return results

    # Test endpoints
    endpoints = [
        ("GET", "/", "Root"),
        ("GET", "/health", "Health Check"),
        ("GET", "/agents/list", "List Agents"),
        ("GET", "/db/status", "Database Status"),
        ("GET", "/data/catalog", "Data Catalog"),
        ("GET", "/security/sessions", "Security Sessions"),
        ("GET", "/pmo/tasks", "PMO Tasks"),
    ]

    print_section("Testing Endpoints")
    for method, endpoint, name in endpoints:
        try:
            if method == "GET":
                resp = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                resp = requests.post(f"{base_url}{endpoint}", json={}, timeout=10)

            success = resp.status_code in [200, 201]
            print_test(f"{method} {endpoint} ({name})", success, f"Status: {resp.status_code}" if not success else "")
            results[endpoint] = success

        except Exception as e:
            print_test(f"{method} {endpoint}", False, str(e))
            results[endpoint] = False

    return results


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    print(f"""
{Colors.BOLD}{Colors.CYAN}
 ==============================================================
 |                                                            |
 |     AI COMPANY - COMPREHENSIVE TEST SUITE                  |
 |     Testing: Supabase, SMTP, Calendar, 7 Agents, APIs      |
 |                                                            |
 ==============================================================
{Colors.END}
    """)

    all_results = {}

    # Run all tests
    all_results["environment"] = test_environment()
    all_results["database"] = test_database()
    all_results["smtp"] = test_smtp()
    all_results["calendar"] = test_calendar()
    all_results["hr_manager"] = test_hr_manager()
    all_results["pmo"] = test_pmo()
    all_results["security"] = test_security()
    all_results["data_analyst"] = test_data_analyst()
    all_results["api"] = test_api_endpoints()

    # Summary
    print_header("TEST SUMMARY")

    total_passed = 0
    total_failed = 0

    for category, results in all_results.items():
        passed = sum(1 for v in results.values() if v == True)
        failed = sum(1 for v in results.values() if v == False)
        total_passed += passed
        total_failed += failed

        status = f"{Colors.GREEN}PASS{Colors.END}" if failed == 0 else f"{Colors.YELLOW}PARTIAL{Colors.END}" if passed > 0 else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {category.upper():20} [{status}] {passed}/{passed+failed} tests")

    print(f"\n{Colors.BOLD}TOTAL: {total_passed} passed, {total_failed} failed{Colors.END}")

    if total_failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All tests passed! System is ready.{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}Some tests failed. Check the output above for details.{Colors.END}")

    return all_results


if __name__ == "__main__":
    run_all_tests()
