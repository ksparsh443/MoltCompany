"""Create all missing tables in Supabase via Management API"""
import json
import subprocess

def run_sql(sql):
    payload = json.dumps({"query": sql})
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        "https://api.supabase.com/v1/projects/czcowvcanqpzmbrvbwcq/database/query",
        "-H", "Authorization: Bearer sbp_974d8c6d57c1aa3ffb0653d7dc56993c9bb69af0",
        "-H", "Content-Type: application/json",
        "-d", payload
    ], capture_output=True, text=True)
    return result.stdout

SQL = """
-- Data Analyst tables
CREATE TABLE IF NOT EXISTS data_catalog (
    id SERIAL PRIMARY KEY,
    source_id TEXT UNIQUE,
    source_name TEXT,
    source_type TEXT,
    file_path TEXT,
    original_url TEXT,
    row_count INTEGER,
    column_count INTEGER,
    columns TEXT,
    file_size_bytes INTEGER,
    ingested_at TEXT,
    last_queried TEXT,
    query_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS data_query_logs (
    id SERIAL PRIMARY KEY,
    query_id TEXT UNIQUE,
    source_id TEXT,
    query_type TEXT,
    query_text TEXT,
    result_rows INTEGER,
    execution_time_ms INTEGER,
    created_at TEXT,
    user_context TEXT
);

CREATE TABLE IF NOT EXISTS visualization_logs (
    id SERIAL PRIMARY KEY,
    viz_id TEXT UNIQUE,
    source_id TEXT,
    chart_type TEXT,
    title TEXT,
    file_path TEXT,
    created_at TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS dashboards (
    id SERIAL PRIMARY KEY,
    dashboard_id TEXT UNIQUE,
    title TEXT,
    description TEXT,
    sources TEXT,
    file_path TEXT,
    created_at TEXT,
    updated_at TEXT,
    status TEXT DEFAULT 'active'
);

-- Pentest extended tables
CREATE TABLE IF NOT EXISTS pentest_test_cases (
    id SERIAL PRIMARY KEY,
    test_id TEXT UNIQUE,
    session_id TEXT,
    category TEXT,
    test_name TEXT,
    description TEXT,
    severity TEXT DEFAULT 'info',
    status TEXT DEFAULT 'pending',
    result TEXT,
    evidence TEXT,
    request TEXT,
    response TEXT,
    duration_ms INTEGER,
    executed_at TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pentest_vulnerabilities (
    id SERIAL PRIMARY KEY,
    vuln_id TEXT UNIQUE,
    session_id TEXT,
    test_id TEXT,
    title TEXT,
    severity TEXT,
    cvss_score REAL,
    description TEXT,
    evidence TEXT,
    remediation TEXT,
    owasp_category TEXT,
    cwe_id TEXT,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- PMO extended
CREATE TABLE IF NOT EXISTS pmo_meeting_minutes (
    id SERIAL PRIMARY KEY,
    mom_id TEXT UNIQUE,
    meeting_id TEXT,
    title TEXT,
    date TEXT,
    attendees TEXT,
    absentees TEXT,
    agenda_items TEXT,
    discussion_points TEXT,
    decisions TEXT,
    action_items TEXT,
    next_meeting TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- HR tables
CREATE TABLE IF NOT EXISTS candidates (
    id SERIAL PRIMARY KEY,
    candidate_id TEXT UNIQUE,
    name TEXT,
    email TEXT,
    phone TEXT,
    linkedin_url TEXT,
    resume_path TEXT,
    skills TEXT,
    experience_years INTEGER,
    current_company TEXT,
    "current_role" TEXT,
    status TEXT DEFAULT 'new',
    applied_for TEXT,
    match_score REAL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS job_descriptions (
    id SERIAL PRIMARY KEY,
    jd_id TEXT UNIQUE,
    title TEXT,
    department TEXT,
    required_skills TEXT,
    preferred_skills TEXT,
    experience_min INTEGER,
    experience_max INTEGER,
    salary_min REAL,
    salary_max REAL,
    location TEXT,
    remote_policy TEXT,
    description TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS interviews (
    id SERIAL PRIMARY KEY,
    interview_id TEXT UNIQUE,
    candidate_id TEXT,
    jd_id TEXT,
    interviewer TEXT,
    interview_type TEXT,
    scheduled_at TEXT,
    duration_minutes INTEGER,
    meeting_link TEXT,
    status TEXT DEFAULT 'scheduled',
    feedback TEXT,
    rating INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS onboarding (
    id SERIAL PRIMARY KEY,
    onboarding_id TEXT UNIQUE,
    employee_id TEXT,
    employee_name TEXT,
    email TEXT,
    department TEXT,
    role TEXT,
    manager TEXT,
    start_date TEXT,
    contract_path TEXT,
    status TEXT DEFAULT 'pending',
    checklist TEXT,
    systems_provisioned TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    metric_id TEXT UNIQUE,
    employee_id TEXT,
    period TEXT,
    tasks_completed INTEGER,
    tasks_assigned INTEGER,
    avg_completion_time REAL,
    quality_score REAL,
    collaboration_score REAL,
    innovation_score REAL,
    burnout_risk REAL,
    growth_potential REAL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS compliance_alerts (
    id SERIAL PRIMARY KEY,
    alert_id TEXT UNIQUE,
    alert_type TEXT,
    severity TEXT,
    title TEXT,
    description TEXT,
    action_required TEXT,
    due_date TEXT,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TEXT
);

-- Token and meeting tables
CREATE TABLE IF NOT EXISTS token_consumption (
    id SERIAL PRIMARY KEY,
    log_id TEXT UNIQUE,
    agent_name TEXT NOT NULL,
    model_name TEXT NOT NULL,
    model_provider TEXT NOT NULL,
    tokens_in INTEGER DEFAULT 0,
    tokens_out INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    estimated_cost REAL DEFAULT 0.0,
    query_preview TEXT,
    response_preview TEXT,
    session_id TEXT,
    user_id TEXT,
    latency_ms INTEGER DEFAULT 0,
    status TEXT DEFAULT 'success',
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS meeting_transcripts (
    id SERIAL PRIMARY KEY,
    transcript_id TEXT UNIQUE,
    meeting_id TEXT,
    speaker TEXT,
    content TEXT,
    timestamp_offset REAL DEFAULT 0.0,
    confidence REAL DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS meeting_recordings (
    id SERIAL PRIMARY KEY,
    recording_id TEXT UNIQUE,
    meeting_id TEXT,
    status TEXT DEFAULT 'recording',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    total_duration_seconds INTEGER DEFAULT 0,
    transcript_count INTEGER DEFAULT 0,
    auto_mom_generated BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS designation_emails (
    id SERIAL PRIMARY KEY,
    designation TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    name TEXT,
    notification_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- General tables
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name TEXT,
    status TEXT DEFAULT 'active',
    owner TEXT,
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    budget DECIMAL(12,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    title TEXT,
    description TEXT,
    status TEXT DEFAULT 'open',
    priority TEXT DEFAULT 'medium',
    assignee TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
"""

ALTER_SQL = """
ALTER TABLE pentest_sessions ADD COLUMN IF NOT EXISTS started_at TEXT;
ALTER TABLE pentest_sessions ADD COLUMN IF NOT EXISTS completed_at TEXT;
ALTER TABLE pentest_sessions ADD COLUMN IF NOT EXISTS total_tests INTEGER DEFAULT 0;
ALTER TABLE pentest_sessions ADD COLUMN IF NOT EXISTS passed_tests INTEGER DEFAULT 0;
ALTER TABLE pentest_sessions ADD COLUMN IF NOT EXISTS failed_tests INTEGER DEFAULT 0;
ALTER TABLE pentest_sessions ADD COLUMN IF NOT EXISTS findings_count INTEGER DEFAULT 0;

ALTER TABLE employees ADD COLUMN IF NOT EXISTS hire_date TIMESTAMPTZ;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS manager_email TEXT;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS start_date TEXT;

ALTER TABLE pmo_tasks ADD COLUMN IF NOT EXISTS reporter TEXT;
ALTER TABLE pmo_tasks ADD COLUMN IF NOT EXISTS tags TEXT;
ALTER TABLE pmo_tasks ADD COLUMN IF NOT EXISTS parent_task TEXT;
ALTER TABLE pmo_tasks ADD COLUMN IF NOT EXISTS blockers TEXT;
ALTER TABLE pmo_tasks ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ;

ALTER TABLE pmo_sprints ADD COLUMN IF NOT EXISTS velocity INTEGER DEFAULT 0;
ALTER TABLE pmo_sprints ADD COLUMN IF NOT EXISTS committed_points INTEGER DEFAULT 0;
ALTER TABLE pmo_sprints ADD COLUMN IF NOT EXISTS completed_points INTEGER DEFAULT 0;

ALTER TABLE pipeline_runs ADD COLUMN IF NOT EXISTS started_at TIMESTAMPTZ;
ALTER TABLE pipeline_runs ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ;
ALTER TABLE pipeline_runs ADD COLUMN IF NOT EXISTS total_checks INTEGER DEFAULT 0;
ALTER TABLE pipeline_runs ADD COLUMN IF NOT EXISTS passed_checks INTEGER DEFAULT 0;
ALTER TABLE pipeline_runs ADD COLUMN IF NOT EXISTS failed_checks INTEGER DEFAULT 0;
"""

print("Creating tables...")
result = run_sql(SQL)
print(f"Tables result: {result[:200]}")

print("\nAltering tables...")
result = run_sql(ALTER_SQL)
print(f"Alter result: {result[:200]}")

print("\nVerifying...")
tables = run_sql("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;")
import json as j
table_list = j.loads(tables)
print(f"\nTotal tables: {len(table_list)}")
for t in table_list:
    print(f"  - {t['tablename']}")
