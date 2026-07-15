-- Run once after PostgreSQL is installed:
--   psql postgres -c "CREATE DATABASE company_research;"
--   psql company_research -c "CREATE EXTENSION IF NOT EXISTS vector;"

-- LangChain PGVector creates langchain_pg_* tables automatically during ingestion.
-- This table is separate relational storage for evaluation history.
CREATE TABLE IF NOT EXISTS resume_evaluation_history (
    id SERIAL PRIMARY KEY,
    company TEXT NOT NULL,
    rating TEXT NOT NULL,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resume_snapshot TEXT NOT NULL
);
