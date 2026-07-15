from pathlib import Path

# Shared RAG settings used by ingestion, retrieval, and vector-store setup.
RAG_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = RAG_DIR / "documents"
CHROMA_DB_DIR = RAG_DIR / "chroma_db"
COLLECTION_NAME = "job_postings"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50

# Stage 2: PostgreSQL + pgvector (override via backend/.env)
DEFAULT_DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/company_research"
