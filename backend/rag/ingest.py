from typing import List, Tuple

from langchain_core.documents import Document

from rag.config import CHUNK_OVERLAP, CHUNK_SIZE, DOCUMENTS_DIR, EMBEDDING_MODEL_NAME
from rag.vectorstore import get_pgvector_store, reset_vectorstore_cache


def parse_company_name(file_stem: str) -> str:
    """Parse company name from filename stem.

    Expected naming example:
    - google__swe_intern_2026.txt -> company: google
    - google_swe_intern.txt -> company: google

    Fallback behavior:
    - If no explicit separator exists, use the first token before an underscore or hyphen.
    """
    if "__" in file_stem:
        company_part = file_stem.split("__", 1)[0]
    else:
        company_part = file_stem.split("_", 1)[0].split("-", 1)[0]

    normalized = company_part.replace("_", " ").replace("-", " ").strip()
    return " ".join(normalized.split()) or "unknown"


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Chunk text into overlapping windows for better semantic retrieval coverage."""
    cleaned_text = " ".join(text.split())
    if not cleaned_text:
        return []

    chunks: List[str] = []
    start = 0

    while start < len(cleaned_text):
        end = min(start + chunk_size, len(cleaned_text))
        chunk = cleaned_text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(cleaned_text):
            break

        start = max(0, end - overlap)

    return chunks


def load_documents() -> List[Tuple[str, str, str]]:
    """Load all .txt job postings and return (filename, company, text) tuples."""
    if not DOCUMENTS_DIR.exists():
        return []

    records: List[Tuple[str, str, str]] = []
    for file_path in sorted(DOCUMENTS_DIR.glob("*.txt")):
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        company = parse_company_name(file_path.stem)
        records.append((file_path.name, company, text))

    return records


def ingest_documents() -> None:
    """Ingest all posting files into PostgreSQL pgvector via LangChain PGVector."""
    document_records = load_documents()
    if not document_records:
        print(f"No .txt files found in: {DOCUMENTS_DIR}")
        return

    documents: List[Document] = []
    ids: List[str] = []

    for filename, company, text in document_records:
        file_chunks = chunk_text(text)
        for idx, chunk in enumerate(file_chunks):
            ids.append(f"{filename}:{idx}")
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": filename,
                        "company": company,
                        "chunk_index": idx,
                    },
                )
            )

    if not documents:
        print("No chunkable text content found in input documents.")
        return

    print(f"Generating embeddings with model: {EMBEDDING_MODEL_NAME}")
    print("Writing chunks to PostgreSQL pgvector via LangChain PGVector")

    vectorstore = get_pgvector_store(pre_delete_collection=True)
    vectorstore.add_documents(documents, ids=ids)
    reset_vectorstore_cache()

    print(
        f"Ingestion complete. Documents: {len(document_records)}, Chunks: {len(documents)}"
    )


if __name__ == "__main__":
    ingest_documents()
