"""PostgreSQL helpers for pgvector and resume-evaluation history."""

import json
import os
from datetime import datetime, timezone
from typing import Any, Optional

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

from rag.config import DEFAULT_DATABASE_URL

load_dotenv(dotenv_path="backend/.env")

HISTORY_TABLE = "resume_evaluation_history"


def get_database_url() -> str:
    """Return the SQLAlchemy/psycopg connection string for Postgres."""
    return os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)


def get_psycopg_dsn() -> str:
    """Convert a SQLAlchemy URL into a psycopg2-compatible DSN."""
    url = get_database_url()
    return url.replace("postgresql+psycopg://", "postgresql://", 1)


def get_connection():
    """Open a psycopg2 connection for simple relational SQL."""
    return psycopg2.connect(get_psycopg_dsn())


def init_history_table() -> None:
    """Create the resume evaluation history table if it does not exist."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {HISTORY_TABLE} (
                    id SERIAL PRIMARY KEY,
                    company TEXT NOT NULL,
                    rating TEXT NOT NULL,
                    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    resume_snapshot TEXT NOT NULL
                )
                """
            )
        conn.commit()


def save_evaluation_history(company: str, rating: str, resume_snapshot: str) -> int:
    """Insert a resume evaluation record and return the new row id."""
    init_history_table()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {HISTORY_TABLE} (company, rating, evaluated_at, resume_snapshot)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (company, rating, datetime.now(timezone.utc), resume_snapshot),
            )
            row_id = cur.fetchone()[0]
        conn.commit()
    return row_id


def get_evaluation_history(company: Optional[str] = None, limit: int = 20) -> list[dict[str, Any]]:
    """Fetch recent evaluation history, optionally filtered by company."""
    init_history_table()
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if company:
                cur.execute(
                    f"""
                    SELECT id, company, rating, evaluated_at, resume_snapshot
                    FROM {HISTORY_TABLE}
                    WHERE company = %s
                    ORDER BY evaluated_at DESC
                    LIMIT %s
                    """,
                    (company, limit),
                )
            else:
                cur.execute(
                    f"""
                    SELECT id, company, rating, evaluated_at, resume_snapshot
                    FROM {HISTORY_TABLE}
                    ORDER BY evaluated_at DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
            return [dict(row) for row in cur.fetchall()]


def resume_to_snapshot(resume: Any) -> str:
    """Serialize resume payload to a storable text snapshot."""
    if isinstance(resume, str):
        return resume
    return json.dumps(resume, ensure_ascii=True, sort_keys=True)


def count_vector_chunks() -> int:
    """Return the number of rows in the LangChain pgvector embedding table."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM langchain_pg_embedding")
            return int(cur.fetchone()[0])


def sample_vector_chunk() -> Optional[dict[str, Any]]:
    """Return one sample chunk row from the pgvector store for verification."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, document, cmetadata
                FROM langchain_pg_embedding
                LIMIT 1
                """
            )
            row = cur.fetchone()
            return dict(row) if row else None


def list_stored_companies_from_db() -> list[str]:
    """Return distinct company names stored in pgvector metadata."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT LOWER(cmetadata->>'company') AS company
                FROM langchain_pg_embedding
                WHERE cmetadata->>'company' IS NOT NULL
                """
            )
            companies = [row[0] for row in cur.fetchall() if row[0]]
    return sorted(set(companies), key=len, reverse=True)
