-- Run this in Supabase Dashboard -> SQL Editor -> New Query -> Run
CREATE TABLE IF NOT EXISTS pmo_tasks (
    id SERIAL PRIMARY KEY, task_id TEXT UNIQUE, title TEXT NOT NULL, description TEXT,
    project TEXT, assignee TEXT, priority TEXT DEFAULT 'medium', status TEXT DEFAULT 'open',
    due_date TEXT, sprint TEXT, story_points INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(), updated_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS pmo_meetings (
    id SERIAL PRIMARY KEY, meeting_id TEXT UNIQUE, title TEXT NOT NULL, meeting_type TEXT,
    scheduled_at TEXT, duration_minutes INTEGER DEFAULT 60, attendees TEXT, agenda TEXT,
    status TEXT DEFAULT 'scheduled', ics_file TEXT, created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS pmo_standups (
    id SERIAL PRIMARY KEY, standup_id TEXT UNIQUE, team_member TEXT, project TEXT,
    yesterday TEXT, today TEXT, blockers TEXT, recorded_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS pmo_action_items (
    id SERIAL PRIMARY KEY, action_id TEXT UNIQUE, meeting_id TEXT, description TEXT,
    assignee TEXT, due_date TEXT, status TEXT DEFAULT 'pending', created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY, employee_id TEXT UNIQUE, name TEXT NOT NULL, email TEXT,
    role TEXT, department TEXT, manager_email TEXT, start_date TEXT,
    status TEXT DEFAULT 'active', created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS pmo_sprints (
    id SERIAL PRIMARY KEY, sprint_id TEXT UNIQUE, name TEXT, project TEXT,
    start_date TEXT, end_date TEXT, status TEXT DEFAULT 'planned', goal TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS pentest_sessions (
    id SERIAL PRIMARY KEY, session_id TEXT UNIQUE, target_url TEXT, target_type TEXT,
    scope TEXT, status TEXT DEFAULT 'active', created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS pentest_tests (
    id SERIAL PRIMARY KEY, test_id TEXT UNIQUE, session_id TEXT, test_name TEXT,
    category TEXT, status TEXT DEFAULT 'pending', result TEXT, details TEXT,
    severity TEXT, created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS security_findings (
    id SERIAL PRIMARY KEY, finding_id TEXT UNIQUE, session_id TEXT, test_name TEXT,
    severity TEXT, description TEXT, details TEXT, status TEXT DEFAULT 'open',
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id SERIAL PRIMARY KEY, pipeline_id TEXT UNIQUE, project_id TEXT, pipeline_name TEXT,
    status TEXT DEFAULT 'pending', stages TEXT, created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS test_cases (
    id SERIAL PRIMARY KEY, test_id TEXT UNIQUE, pipeline_id TEXT, test_name TEXT,
    test_type TEXT, status TEXT DEFAULT 'pending', result TEXT, details TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
