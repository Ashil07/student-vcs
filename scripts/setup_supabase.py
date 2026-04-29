#!/usr/bin/env python3
"""
Run this once to create the PostgreSQL schema in your Supabase project.
Requires SUPABASE_URL and SUPABASE_SERVICE_KEY in environment.
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("Error: Set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env")
    sys.exit(1)

# Extract host from URL: https://xxx.supabase.co
host = SUPABASE_URL.replace("https://", "").replace("http://", "")
# Supabase connection uses port 5432, password from service key is the JWT token itself
# Actually for direct Postgres, we need the DB password from Supabase dashboard
# But we can use the Supabase client to run RPC instead

from supabase import create_client

client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

schema_sql = """
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Repositories table (namespaced by user)
CREATE TABLE IF NOT EXISTS repos (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, name)
);

-- Branches
CREATE TABLE IF NOT EXISTS branches (
    id SERIAL PRIMARY KEY,
    repo_id INTEGER NOT NULL REFERENCES repos(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    commit_id TEXT,
    is_current INTEGER DEFAULT 0,
    UNIQUE(repo_id, name)
);

-- Commits
CREATE TABLE IF NOT EXISTS commits (
    id TEXT PRIMARY KEY,
    repo_id INTEGER NOT NULL REFERENCES repos(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    parent_ids JSONB NOT NULL DEFAULT '[]',
    branch_id INTEGER REFERENCES branches(id) ON DELETE SET NULL
);

-- Commit files (content-addressed storage links)
CREATE TABLE IF NOT EXISTS commit_files (
    commit_id TEXT NOT NULL REFERENCES commits(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    PRIMARY KEY (commit_id, file_path)
);

-- Staging area
CREATE TABLE IF NOT EXISTS staging (
    repo_id INTEGER NOT NULL REFERENCES repos(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    PRIMARY KEY (repo_id, file_path)
);

-- Config per repo
CREATE TABLE IF NOT EXISTS config (
    repo_id INTEGER NOT NULL REFERENCES repos(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY (repo_id, key)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_commits_repo ON commits(repo_id);
CREATE INDEX IF NOT EXISTS idx_commits_branch ON commits(branch_id);
CREATE INDEX IF NOT EXISTS idx_commit_files_hash ON commit_files(file_hash);
CREATE INDEX IF NOT EXISTS idx_branches_repo ON branches(repo_id);

-- Row Level Security: users can only see their own repos
ALTER TABLE repos ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_repos ON repos
    FOR ALL
    USING (auth.uid() = user_id);

-- Enable RLS on other tables (via repo_id FK cascade)
ALTER TABLE branches ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_branches ON branches
    FOR ALL
    USING (repo_id IN (SELECT id FROM repos WHERE user_id = auth.uid()));

ALTER TABLE commits ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_commits ON commits
    FOR ALL
    USING (repo_id IN (SELECT id FROM repos WHERE user_id = auth.uid()));

ALTER TABLE commit_files ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_commit_files ON commit_files
    FOR ALL
    USING (commit_id IN (SELECT id FROM commits WHERE repo_id IN (SELECT id FROM repos WHERE user_id = auth.uid())));

ALTER TABLE staging ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_staging ON staging
    FOR ALL
    USING (repo_id IN (SELECT id FROM repos WHERE user_id = auth.uid()));

ALTER TABLE config ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_config ON config
    FOR ALL
    USING (repo_id IN (SELECT id FROM repos WHERE user_id = auth.uid()));
"""

def main():
    print("Connecting to Supabase...")
    # Use Supabase REST SQL execution via RPC
    # For direct SQL, we need to connect to PostgreSQL directly
    # The connection string can be found in Supabase dashboard: Database > Connection String

    db_password = input("Enter your Supabase database password (from Settings > Database): ")
    db_host = SUPABASE_URL.replace("https://", "").replace("http://", "")
    conn_str = f"postgresql://postgres:{db_password}@db.{db_host}:5432/postgres"

    print(f"Connecting to PostgreSQL at db.{db_host}...")
    conn = psycopg2.connect(conn_str)
    cursor = conn.cursor()

    print("Creating schema...")
    cursor.execute(schema_sql)
    conn.commit()
    conn.close()

    print("Schema created successfully!")
    print("Next steps:")
    print("1. Set USE_SUPABASE=true in your .env")
    print("2. Restart your API server")
    print("3. Create an account via the React UI or Supabase auth")


if __name__ == "__main__":
    main()
