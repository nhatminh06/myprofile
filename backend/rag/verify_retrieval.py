#!/usr/bin/env python3
"""Verify pgvector ingestion and retrieval after PostgreSQL setup."""

from rag.db import count_vector_chunks, sample_vector_chunk
from rag.retrieve import retrieve_relevant_chunks


def main() -> None:
    chunk_count = count_vector_chunks()
    sample = sample_vector_chunk()
    print(f"Vector chunk row count: {chunk_count}")
    if sample:
        print("Sample row:")
        print(f"  id: {sample.get('id')}")
        print(f"  document: {str(sample.get('document', ''))[:200]}...")
        print(f"  cmetadata: {sample.get('cmetadata')}")

    queries = [
        ("Copart", None, "company name"),
        ("Copart", "DevOps internship requirements at Copart", "reworded query"),
        ("Copart", "Python machine learning experience required", "content-based without company name"),
    ]

    for company, qtext, label in queries:
        result = retrieve_relevant_chunks(company, top_k=3, query_text=qtext)
        print(f"\n=== {label} ===")
        print(result[:500] if result else "(empty)")
        print("chunks:", result.count("[Chunk"))
        print("source attribution:", "source:" in result and "company:" in result)


if __name__ == "__main__":
    main()
