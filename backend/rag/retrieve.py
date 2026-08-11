from typing import List, Optional

from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.prompts import ChatPromptTemplate

from rag.vectorstore import get_vectorstore_retriever, list_stored_companies


def normalize_company_name(company: str) -> str:
    """Normalize a company string so metadata matching is consistent."""
    normalized = company.strip().lower().replace("__", " ").replace("_", " ").replace("-", " ")
    return " ".join(normalized.split())


def extract_company_filter(query_text: str) -> str:
    """Pick the most likely company token from a natural-language query."""
    normalized_query = normalize_company_name(query_text)
    for company_name in list_stored_companies():
        if company_name and company_name in normalized_query:
            return company_name
    return normalized_query


def _format_documents(documents: List[Document]) -> str:
    """Format retrieved LangChain documents with source attribution."""
    if not documents:
        return ""

    formatted_chunks: List[str] = []
    for idx, doc in enumerate(documents, start=1):
        metadata = doc.metadata or {}
        source = metadata.get("source", "unknown")
        company_name = metadata.get("company", "unknown")
        formatted_chunks.append(
            f"[Chunk {idx} | source: {source} | company: {company_name}]\n{doc.page_content.strip()}"
        )

    return "\n\n".join(formatted_chunks)


def _build_retrieval_chain(top_k: int, company_filter: Optional[str] = None):
    """Create a LangChain retrieval chain backed by a VectorStoreRetriever.

    The chain uses a stub LLM so retrieval can be tested without a real API key.
    Downstream nodes consume the retrieved context, not the chain's answer field.
    """
    retriever = get_vectorstore_retriever(top_k=top_k, company_filter=company_filter)

    # Stub LLM: create_retrieval_chain requires an LLM step, but we only need context.
    llm = FakeListChatModel(responses=["retrieval-only stub"])

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Use the retrieved job posting context to answer the question.\n\n{context}",
            ),
            ("human", "{input}"),
        ]
    )
    document_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, document_chain)


def retrieve_relevant_chunks(company: str, top_k: int = 5, query_text: Optional[str] = None) -> str:
    """Retrieve and format top-k relevant qualification chunks via LangChain's retrieval chain."""
    if not company or not company.strip():
        return ""

    company_filter = extract_company_filter(company)
    query_text = query_text or f"{company.strip()} software engineer intern qualifications"

    # Prefer an exact metadata filter so results stay inside the target company's document set.
    chain = _build_retrieval_chain(top_k=top_k, company_filter=company_filter)
    result = chain.invoke({"input": query_text})
    documents: List[Document] = result.get("context") or []

    # If no chunks exist for the filtered company, fall back to the broader corpus.
    if not documents:
        fallback_chain = _build_retrieval_chain(top_k=top_k)
        result = fallback_chain.invoke({"input": query_text})
        documents = result.get("context") or []

    return _format_documents(documents)
