# RAG Job Posting Store

This folder contains a local Retrieval-Augmented Generation (RAG) pipeline for resume evaluation.

## PostgreSQL + pgvector Setup (required)

Run these commands locally before ingestion:

```bash
brew install postgresql@16 pgvector
brew services start postgresql@16

# Create role/database if needed (adjust password to match backend/.env)
createuser -s postgres || true
createdb company_research || true

psql company_research -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

Verify Postgres is ready:

```bash
psql company_research -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"
```

Set `DATABASE_URL` in `backend/.env` (default):

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/company_research
```

## Add New Job Postings

1. Drop one or more `.txt` files into `backend/rag/documents/`.
2. Re-run ingestion:

```bash
cd backend
uv run python rag/ingest.py
```

3. Verify storage and retrieval:

```bash
uv run python rag/verify_retrieval.py
```

## How Chunking and Embedding Works

- Ingestion reads all `.txt` files in `documents/`.
- Each document is chunked into overlapping character windows (`CHUNK_SIZE=400`, `CHUNK_OVERLAP=50`).
- Each chunk is embedded using `sentence-transformers` model `all-MiniLM-L6-v2`.
- Chunks are stored in PostgreSQL pgvector via LangChain's `PGVector` class.
- Metadata includes `source`, `company`, and `chunk_index`.

## Retrieval Chain

Retrieval uses LangChain's `create_retrieval_chain` (from `langchain-classic`) with a `VectorStoreRetriever` backed by PGVector. The LangGraph node structure remains `retrieve -> rate -> advise`.

## Evaluation History Table

Relational history (non-vector) is stored in `resume_evaluation_history` via simple SQL in `backend/rag/db.py`:

- `company`
- `rating`
- `evaluated_at`
- `resume_snapshot`

The SQL schema is also in `backend/rag/setup_postgres.sql`.
