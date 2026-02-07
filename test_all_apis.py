# -*- coding: utf-8 -*-
"""
Comprehensive API Test Suite - Tests EVERY endpoint in api_server.py
Stores detailed results in agent_workspace/test_results/
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta

os.environ['PYTHONUTF8'] = '1'

BASE_URL = "http://localhost:8000"
RESULTS = []
PASS_COUNT = 0
FAIL_COUNT = 0
SKIP_COUNT = 0


def test(name, method, endpoint, **kwargs):
    """Run a single API test and record result"""
    global PASS_COUNT, FAIL_COUNT, SKIP_COUNT
    url = f"{BASE_URL}{endpoint}"
    start = time.time()
    result = {
        "name": name,
        "method": method,
        "endpoint": endpoint,
        "url": url,
        "timestamp": datetime.utcnow().isoformat(),
    }

    try:
        timeout = kwargs.pop("timeout", 60)
        if method == "GET":
            resp = requests.get(url, params=kwargs.get("params"), timeout=timeout)
        elif method == "POST":
            if kwargs.get("data"):
                resp = requests.post(url, data=kwargs["data"], timeout=timeout)
            else:
                resp = requests.post(url, json=kwargs.get("json", {}), params=kwargs.get("params"), timeout=timeout)
        elif method == "SKIP":
            result["status"] = "SKIP"
            result["reason"] = kwargs.get("reason", "Skipped")
            result["elapsed_ms"] = 0
            RESULTS.append(result)
            SKIP_COUNT += 1
            print(f"  [SKIP] {name} - {result['reason']}")
            return result

        elapsed = round((time.time() - start) * 1000, 1)
        result["status_code"] = resp.status_code
        result["elapsed_ms"] = elapsed

        try:
            result["response"] = resp.json()
        except Exception:
            result["response"] = resp.text[:500]

        if resp.status_code in [200, 201]:
            result["status"] = "PASS"
            PASS_COUNT += 1
            print(f"  [PASS] {name} ({resp.status_code}, {elapsed}ms)")
        else:
            result["status"] = "FAIL"
            FAIL_COUNT += 1
            detail = ""
            try:
                detail = resp.json().get("detail", "")[:100]
            except Exception:
                detail = resp.text[:100]
            print(f"  [FAIL] {name} ({resp.status_code}, {elapsed}ms) - {detail}")

    except requests.exceptions.ConnectionError:
        result["status"] = "FAIL"
        result["error"] = "Connection refused - server not running"
        result["elapsed_ms"] = round((time.time() - start) * 1000, 1)
        FAIL_COUNT += 1
        print(f"  [FAIL] {name} - Connection refused")
    except Exception as e:
        result["status"] = "FAIL"
        result["error"] = str(e)[:200]
        result["elapsed_ms"] = round((time.time() - start) * 1000, 1)
        FAIL_COUNT += 1
        print(f"  [FAIL] {name} - {str(e)[:80]}")

    RESULTS.append(result)
    return result


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ============================================================================
# TEST EXECUTION
# ============================================================================

def run_all():
    global PASS_COUNT, FAIL_COUNT, SKIP_COUNT

    print("""
============================================================
     AI COMPANY - COMPREHENSIVE API TEST SUITE
     Testing ALL endpoints in api_server.py
============================================================
""")

    # ------------------------------------------------------------------
    section("1. GENERAL ENDPOINTS")
    # ------------------------------------------------------------------
    test("Root", "GET", "/")
    test("Health Check", "GET", "/health")
    test("List Agents", "GET", "/agents/list")
    test("System Stats", "GET", "/stats")

    # ------------------------------------------------------------------
    section("2. DATABASE & SYSTEM")
    # ------------------------------------------------------------------
    test("Database Status", "GET", "/db/status")
    test("Database Schema", "GET", "/db/schema")
    test("Email Config Status", "GET", "/email/config-status")
    test("Test Email (simulated)", "POST", "/email/test",
         params={"to_email": "test@example.com", "subject": "API Test", "body": "Test email body"})

    # ------------------------------------------------------------------
    section("3. HR MANAGER")
    # ------------------------------------------------------------------
    test("Search Candidates", "POST", "/hr/search-candidates",
         json={"job_title": "Python Developer", "skills": "Python, FastAPI", "location": "Remote", "num_results": 3})
    test("Onboard Employee", "POST", "/hr/onboard",
         json={
             "employee_name": "Test Employee",
             "email": "test.employee@example.com",
             "role": "Software Engineer",
             "department": "Engineering",
             "manager_email": "manager@example.com",
             "start_date": (datetime.utcnow() + timedelta(days=14)).strftime("%Y-%m-%d")
         })
    test("List Employees", "GET", "/hr/employees")
    test("List Employees (filtered)", "GET", "/hr/employees", params={"department": "Engineering", "status": "active"})

    # ------------------------------------------------------------------
    section("4. PMO / SCRUM MASTER")
    # ------------------------------------------------------------------
    task_result = test("Create Task", "POST", "/pmo/tasks",
         json={
             "title": "API Test Task",
             "description": "Created by comprehensive API test suite",
             "project": "TestProject",
             "assignee": "tester@example.com",
             "priority": "high",
             "due_date": (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d"),
             "sprint": "Sprint-1",
             "story_points": 5
         })
    test("Get All Tasks", "GET", "/pmo/tasks")
    test("Get Tasks (filtered by project)", "GET", "/pmo/tasks", params={"project": "TestProject"})
    test("Get Tasks (filtered by sprint)", "GET", "/pmo/tasks", params={"sprint": "Sprint-1"})
    test("Get Tasks (filtered by status)", "GET", "/pmo/tasks", params={"status": "open"})

    meeting_result = test("Schedule Meeting", "POST", "/pmo/meetings",
         json={
             "title": "API Test Meeting",
             "meeting_type": "standup",
             "scheduled_at": (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%dT10:00:00"),
             "duration_minutes": 30,
             "attendees": "dev@example.com,pm@example.com",
             "agenda": "Test meeting from API test suite"
         })

    # Try to download ICS if meeting was created
    meeting_id = ""
    if meeting_result.get("status") == "PASS" and meeting_result.get("response"):
        meeting_id = meeting_result["response"].get("meeting_id", "")
    if meeting_id:
        test("Download Meeting ICS", "GET", f"/pmo/meetings/{meeting_id}/ics")
    else:
        test("Download Meeting ICS", "SKIP", "/pmo/meetings/MTG-xxx/ics", reason="No meeting_id from previous test")

    test("Create Excel Tracker", "POST", "/pmo/excel-tracker",
         params={"tracker_name": "APITestTracker", "tracker_type": "sprint", "project": "TestProject"})

    # ------------------------------------------------------------------
    section("5. SECURITY PENTESTER")
    # ------------------------------------------------------------------
    session_result = test("Create Pentest Session", "POST", "/security/pentest/session",
         json={
             "target_url": "https://httpbin.org",
             "target_type": "web_application",
             "scope": "API test scope"
         })

    session_id = ""
    if session_result.get("status") == "PASS" and session_result.get("response"):
        session_id = session_result["response"].get("session_id", "")

    if session_id:
        test("Run Security Scan", "POST", "/security/pentest/scan",
             json={"session_id": session_id, "scan_type": "quick", "test_categories": ["web"]})
        test("Get Pentest Results", "GET", f"/security/pentest/{session_id}/results")
        test("Generate Pentest Report", "GET", f"/security/pentest/{session_id}/report",
             params={"format": "markdown"})
    else:
        test("Run Security Scan", "SKIP", "/security/pentest/scan", reason="No session_id")
        test("Get Pentest Results", "SKIP", "/security/pentest/xxx/results", reason="No session_id")
        test("Generate Pentest Report", "SKIP", "/security/pentest/xxx/report", reason="No session_id")

    test("List Security Sessions", "GET", "/security/sessions")
    test("List Security Sessions (filtered)", "GET", "/security/sessions",
         params={"target_url": "httpbin.org", "status": "active"})

    # ------------------------------------------------------------------
    section("6. DATA ANALYST")
    # ------------------------------------------------------------------
    test("Get Data Catalog", "GET", "/data/catalog")
    test("List Dashboards", "GET", "/data/dashboards")

    # Create sample CSV for ingestion
    sample_csv = os.path.join(os.path.dirname(__file__), "agent_workspace", "data_analyst", "api_test_data.csv")
    os.makedirs(os.path.dirname(sample_csv), exist_ok=True)
    with open(sample_csv, "w") as f:
        f.write("month,revenue,region\nJan,10000,North\nFeb,12000,South\nMar,15000,East\nApr,18000,West\n")

    ingest_result = test("Ingest Data File", "POST", "/data/ingest",
         json={"file_path": sample_csv, "source_name": "API Test Data", "file_type": "csv"})

    source_id = ""
    if ingest_result.get("status") == "PASS" and ingest_result.get("response"):
        source_id = ingest_result["response"].get("source_id", "")

    if source_id:
        test("Query Data (SQL)", "POST", "/data/query",
             json={"source_id": source_id, "query": "SELECT * FROM data", "query_type": "sql"})
        test("Create Chart", "POST", "/data/chart",
             json={
                 "source_id": source_id,
                 "chart_type": "bar",
                 "x_column": "month",
                 "y_column": "revenue",
                 "title": "API Test Chart",
                 "aggregation": "none"
             })
        test("Create Dashboard", "POST", "/data/dashboard",
             json={
                 "title": "API Test Dashboard",
                 "description": "Created by test suite",
                 "source_ids": source_id,
                 "charts_config": json.dumps([{"type": "bar", "x": "month", "y": "revenue", "title": "Revenue"}])
             })
    else:
        test("Query Data", "SKIP", "/data/query", reason="No source_id from ingestion")
        test("Create Chart", "SKIP", "/data/chart", reason="No source_id")
        test("Create Dashboard", "SKIP", "/data/dashboard", reason="No source_id")

    # ------------------------------------------------------------------
    section("7. TOKEN MONITORING")
    # ------------------------------------------------------------------
    test("Get Token Consumption", "GET", "/tokens/consumption")
    test("Get Token Consumption (filtered)", "GET", "/tokens/consumption",
         params={"agent_name": "HR_Manager", "days": 30})
    test("Get Token Summary", "GET", "/tokens/summary")

    # ------------------------------------------------------------------
    section("8. MEETING RECORDER")
    # ------------------------------------------------------------------
    rec_meeting_id = f"MTG-TEST-{int(time.time())}"
    test("Start Meeting Recording", "POST", f"/meetings/recording/start/{rec_meeting_id}")
    test("Add Transcript Chunk", "POST", "/meetings/recording/transcript",
         json={
             "meeting_id": rec_meeting_id,
             "speaker": "Test Speaker",
             "content": "This is a test transcript from the API test suite.",
             "confidence": 0.95
         })
    test("Add Transcript Chunk 2", "POST", "/meetings/recording/transcript",
         json={
             "meeting_id": rec_meeting_id,
             "speaker": "Another Speaker",
             "content": "I agree with the previous point. Let's move forward.",
             "confidence": 0.88
         })
    test("Get Meeting Transcript", "GET", f"/meetings/recording/{rec_meeting_id}/transcript")
    test("Get Active Recordings", "GET", "/meetings/recording/active")
    test("Stop Meeting Recording", "POST", f"/meetings/recording/stop/{rec_meeting_id}",
         params={"auto_mom": "true"})
    test("Meeting Recorder Page", "GET", "/meeting-recorder", params={"meeting_id": "TEST-123"})

    # ------------------------------------------------------------------
    section("9. DESIGNATION EMAIL MANAGEMENT")
    # ------------------------------------------------------------------
    test("Set Designation Email", "POST", "/designations/set",
         json={"designation": "cto", "email": "cto@example.com", "name": "Test CTO"})
    test("Set Designation Email 2", "POST", "/designations/set",
         json={"designation": "hr_lead", "email": "hr@example.com", "name": "Test HR Lead"})
    test("Resolve Designation (exists)", "GET", "/designations/resolve/cto")
    test("Resolve Designation (missing)", "GET", "/designations/resolve/nonexistent_role")
    test("Notify Designation", "POST", "/designations/notify",
         params={"designation": "cto", "subject": "API Test Notification", "body": "This is a test notification."})

    # ------------------------------------------------------------------
    section("10. MARKETING")
    # ------------------------------------------------------------------
    test("Enhance Post with AI", "POST", "/marketing/enhance",
         json={
             "content": "We just launched our new AI-powered analytics platform!",
             "platform": "linkedin",
             "tone": "professional",
             "add_hashtags": True,
             "add_hook": True,
             "add_cta": True
         })
    test("List Marketing Assets", "GET", "/marketing/assets")
    test("List Marketing Assets (images)", "GET", "/marketing/assets", params={"asset_type": "images"})
    test("Post to Social (dry run)", "POST", "/marketing/post",
         json={
             "content": "Test post from API test suite - please ignore",
             "platforms": "linkedin",
             "hashtags": "#test #api"
         })

    # Skip heavy operations that need real API keys / long execution
    test("Generate Marketing Image", "POST", "/marketing/generate-image",
         json={"prompt": "modern AI technology abstract", "style": "professional", "platform": "linkedin"},
         timeout=120)
    test("Generate Marketing Video", "POST", "/marketing/generate-video",
         json={"prompt": "AI company intro", "duration": 3, "style": "professional", "method": "slideshow"},
         timeout=120)
    test("Auto LinkedIn Post", "POST", "/marketing/auto-linkedin",
         json={
             "topic": "AI innovation in 2026",
             "tone": "professional",
             "generate_image": False,
             "post_immediately": False
         },
         timeout=120)

    # ------------------------------------------------------------------
    section("11. LINKEDIN OAUTH (pages only)")
    # ------------------------------------------------------------------
    test("LinkedIn Setup Page", "GET", "/linkedin/setup")
    test("LinkedIn Save Credentials", "SKIP", "/linkedin/save-credentials", reason="Modifies .env file")
    test("LinkedIn OAuth Callback", "SKIP", "/linkedin/callback", reason="Needs real OAuth flow")

    # ------------------------------------------------------------------
    section("12. GITHUB")
    # ------------------------------------------------------------------
    test("GitHub Status", "GET", "/github/status")

    # ------------------------------------------------------------------
    section("13. CONVERSATION / QUERY")
    # ------------------------------------------------------------------
    test("Get History (empty session)", "GET", "/history/test_session_nonexistent")
    test("Pending Code Files", "GET", "/pending-code")
    test("Query Endpoint (simple)", "POST", "/query",
         json={"query": "What agents are available?", "user_id": "test", "session_id": "api_test_session"},
         timeout=120)

    # 404 is expected for nonexistent file - count as PASS
    r404 = test("Download Approved Code (expect 404)", "GET", "/approved-code/nonexistent.py")
    if r404 and r404.get("status_code") == 404:
        r404["status"] = "PASS"
        r404["note"] = "404 is expected for nonexistent file"
        PASS_COUNT += 1
        FAIL_COUNT -= 1
    test("Knowledge Search", "GET", "/knowledge/search", params={"query": "AI agents", "limit": 3})

    # ------------------------------------------------------------------
    section("14. GOOGLE DRIVE (last - may block server)")
    # ------------------------------------------------------------------
    test("Drive Status", "GET", "/drive/status")
    test("Drive Reload", "POST", "/drive/reload")
    test("Drive Sync", "POST", "/drive/sync", timeout=120)
    test("Drive Folders", "GET", "/drive/folders")

    # ------------------------------------------------------------------
    # PRINT SUMMARY
    # ------------------------------------------------------------------
    print(f"""

{'='*60}
     CONSOLIDATED TEST RESULTS
{'='*60}

  PASSED:  {PASS_COUNT}
  FAILED:  {FAIL_COUNT}
  SKIPPED: {SKIP_COUNT}
  TOTAL:   {len(RESULTS)}

  Success Rate: {round(PASS_COUNT / max(PASS_COUNT + FAIL_COUNT, 1) * 100, 1)}%
{'='*60}
""")

    # Store results
    store_results()

    return RESULTS


def store_results():
    """Store detailed results in agent_workspace/test_results/"""
    results_dir = os.path.join(os.path.dirname(__file__), "agent_workspace", "test_results")
    os.makedirs(results_dir, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    # 1. Full detailed JSON
    full_path = os.path.join(results_dir, f"api_test_full_{timestamp}.json")
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump({
            "test_run": {
                "timestamp": datetime.utcnow().isoformat(),
                "base_url": BASE_URL,
                "total_tests": len(RESULTS),
                "passed": PASS_COUNT,
                "failed": FAIL_COUNT,
                "skipped": SKIP_COUNT,
                "success_rate": round(PASS_COUNT / max(PASS_COUNT + FAIL_COUNT, 1) * 100, 1),
            },
            "results": RESULTS
        }, f, indent=2, default=str)
    print(f"  Full results:    {full_path}")

    # 2. Summary by category
    categories = {}
    for r in RESULTS:
        ep = r["endpoint"]
        if ep.startswith("/hr"): cat = "HR Manager"
        elif ep.startswith("/pmo"): cat = "PMO/Scrum"
        elif ep.startswith("/security"): cat = "Security"
        elif ep.startswith("/data"): cat = "Data Analyst"
        elif ep.startswith("/tokens"): cat = "Token Monitoring"
        elif ep.startswith("/meetings") or ep.startswith("/meeting-recorder"): cat = "Meeting Recorder"
        elif ep.startswith("/designations"): cat = "Designations"
        elif ep.startswith("/drive"): cat = "Google Drive"
        elif ep.startswith("/marketing"): cat = "Marketing"
        elif ep.startswith("/linkedin"): cat = "LinkedIn"
        elif ep.startswith("/github"): cat = "GitHub"
        elif ep.startswith("/db") or ep.startswith("/email"): cat = "Database & System"
        elif ep.startswith("/query") or ep.startswith("/history") or ep.startswith("/pending") or ep.startswith("/approved") or ep.startswith("/knowledge"): cat = "Conversation"
        else: cat = "General"

        if cat not in categories:
            categories[cat] = {"pass": 0, "fail": 0, "skip": 0, "tests": []}
        categories[cat]["tests"].append({"name": r["name"], "status": r["status"], "endpoint": r["endpoint"]})
        if r["status"] == "PASS": categories[cat]["pass"] += 1
        elif r["status"] == "FAIL": categories[cat]["fail"] += 1
        else: categories[cat]["skip"] += 1

    summary_path = os.path.join(results_dir, f"api_test_summary_{timestamp}.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(categories, f, indent=2)
    print(f"  Summary:         {summary_path}")

    # 3. Failures only
    failures = [r for r in RESULTS if r["status"] == "FAIL"]
    if failures:
        fail_path = os.path.join(results_dir, f"api_test_failures_{timestamp}.json")
        with open(fail_path, "w", encoding="utf-8") as f:
            json.dump(failures, f, indent=2, default=str)
        print(f"  Failures:        {fail_path}")

    # 4. Store per-agent results in their respective workspace directories
    agent_dirs = {
        "HR Manager": "hr",
        "PMO/Scrum": "pmo",
        "Security": "security_reports",
        "Data Analyst": "data_analyst",
        "Marketing": "marketing",
    }
    for cat, dirname in agent_dirs.items():
        if cat in categories:
            agent_dir = os.path.join(os.path.dirname(__file__), "agent_workspace", dirname)
            os.makedirs(agent_dir, exist_ok=True)
            agent_path = os.path.join(agent_dir, f"api_test_results_{timestamp}.json")
            with open(agent_path, "w", encoding="utf-8") as f:
                json.dump({
                    "category": cat,
                    "timestamp": datetime.utcnow().isoformat(),
                    "pass": categories[cat]["pass"],
                    "fail": categories[cat]["fail"],
                    "skip": categories[cat]["skip"],
                    "tests": categories[cat]["tests"],
                    "details": [r for r in RESULTS if any(
                        r["endpoint"].startswith(prefix) for prefix in
                        {
                            "HR Manager": ["/hr"],
                            "PMO/Scrum": ["/pmo"],
                            "Security": ["/security"],
                            "Data Analyst": ["/data"],
                            "Marketing": ["/marketing"],
                        }.get(cat, [])
                    )]
                }, f, indent=2, default=str)
            print(f"  {cat} results: {agent_path}")

    # 5. Human-readable markdown report
    md_path = os.path.join(results_dir, f"api_test_report_{timestamp}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# API Test Report\n\n")
        f.write(f"**Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}  \n")
        f.write(f"**Server:** {BASE_URL}  \n")
        f.write(f"**Total:** {len(RESULTS)} tests | **Passed:** {PASS_COUNT} | **Failed:** {FAIL_COUNT} | **Skipped:** {SKIP_COUNT}  \n")
        f.write(f"**Success Rate:** {round(PASS_COUNT / max(PASS_COUNT + FAIL_COUNT, 1) * 100, 1)}%\n\n")

        f.write("## Results by Category\n\n")
        f.write("| Category | Pass | Fail | Skip | Status |\n")
        f.write("|----------|------|------|------|--------|\n")
        for cat, data in sorted(categories.items()):
            status = "PASS" if data["fail"] == 0 else "PARTIAL" if data["pass"] > 0 else "FAIL"
            f.write(f"| {cat} | {data['pass']} | {data['fail']} | {data['skip']} | {status} |\n")

        f.write("\n## Detailed Results\n\n")
        f.write("| # | Endpoint | Method | Status | Time (ms) |\n")
        f.write("|---|----------|--------|--------|----------|\n")
        for i, r in enumerate(RESULTS, 1):
            elapsed = r.get("elapsed_ms", "-")
            status_code = r.get("status_code", "-")
            f.write(f"| {i} | `{r['endpoint']}` | {r.get('method', '-')} | {r['status']} ({status_code}) | {elapsed} |\n")

        if failures:
            f.write("\n## Failures\n\n")
            for r in failures:
                f.write(f"### {r['name']}\n")
                f.write(f"- **Endpoint:** `{r.get('method', '')} {r['endpoint']}`\n")
                f.write(f"- **Status Code:** {r.get('status_code', 'N/A')}\n")
                if r.get("error"):
                    f.write(f"- **Error:** {r['error']}\n")
                if r.get("response") and isinstance(r["response"], dict):
                    f.write(f"- **Detail:** {r['response'].get('detail', 'N/A')}\n")
                f.write("\n")

    print(f"  Report:          {md_path}")


if __name__ == "__main__":
    run_all()
