"""Retrieval agent — searches ChromaDB and falls back to mock SOPs."""

from app.schemas.agent_schema import RetrievalResult
from app.vectorstore.retriever import retrieve_context


async def retrieve_context_for_request(query: str, domain: str) -> RetrievalResult:
    return await retrieve_context(query, domain)
