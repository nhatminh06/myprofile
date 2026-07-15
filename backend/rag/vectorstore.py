"""LangChain PGVector store and retriever factory for the RAG pipeline."""

from functools import lru_cache
from typing import Optional

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_postgres import PGVector

from rag.config import COLLECTION_NAME, EMBEDDING_DIMENSION, EMBEDDING_MODEL_NAME
from rag.db import get_database_url, list_stored_companies_from_db

_embeddings = None
_vectorstore = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return a shared HuggingFace embedding model compatible with ingestion."""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings


def get_pgvector_store(*, pre_delete_collection: bool = False) -> PGVector:
    """Return a LangChain PGVector store backed by PostgreSQL."""
    return PGVector(
        embeddings=get_embeddings(),
        collection_name=COLLECTION_NAME,
        connection=get_database_url(),
        embedding_length=EMBEDDING_DIMENSION,
        use_jsonb=True,
        create_extension=True,
        pre_delete_collection=pre_delete_collection,
    )


@lru_cache(maxsize=1)
def get_vectorstore() -> PGVector:
    """Return a cached PGVector instance for retrieval."""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = get_pgvector_store()
    return _vectorstore


def reset_vectorstore_cache() -> None:
    """Clear cached vector store after re-ingestion."""
    global _vectorstore
    _vectorstore = None
    get_vectorstore.cache_clear()


def get_vectorstore_retriever(
    top_k: int = 5,
    company_filter: Optional[str] = None,
) -> VectorStoreRetriever:
    """Build a LangChain VectorStoreRetriever with optional company metadata filter."""
    search_kwargs: dict = {"k": top_k}
    if company_filter:
        search_kwargs["filter"] = {"company": company_filter}

    return get_vectorstore().as_retriever(
        search_type="similarity",
        search_kwargs=search_kwargs,
    )


def list_stored_companies() -> list[str]:
    """Return distinct company names stored in vector metadata."""
    try:
        return list_stored_companies_from_db()
    except Exception:
        return []
