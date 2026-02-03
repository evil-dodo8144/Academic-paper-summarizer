"""Shared RAG + LLM pipeline for summarizing a PDF."""

from rag.pdf_loader import load_pdf
from rag.chunker import chunk_text
from rag.compressor import compress_chunks
from rag.embeddings import get_embeddings
from rag.vector_store import build_vectorstore
from rag.retriever import get_retriever
from llm.scaledown_client import ScaleDownLLM


ACADEMIC_SUMMARY_INSTRUCTION = """You are summarizing an academic research paper. Preserve technical accuracy: keep key terms, methods, and findings exact. Structure your response clearly (e.g. objective, methods, results, conclusions). Do not invent or add information not present in the excerpts."""


def summarize_pdf(file_path: str, query: str = "Summarize this paper") -> str:
    """
    Extract text from PDF, run RAG (chunk → compress → embed → retrieve), then generate summary.
    Uses compression to handle lengthy papers while preserving technical accuracy.
    """
    text = load_pdf(file_path)
    if not text or not text.strip():
        return "No text could be extracted from the PDF."
    chunks = chunk_text(text)
    compressed = compress_chunks(chunks)
    embeddings = get_embeddings()
    vectorstore = build_vectorstore(compressed, embeddings)
    retriever = get_retriever(vectorstore)
    docs = retriever.get_relevant_documents(query)
    if not docs:
        return "No relevant sections were retrieved. The paper may be too short or the query may not match the content."
    context = "\n\n---\n\n".join(d.page_content for d in docs)
    prompt = f"""{ACADEMIC_SUMMARY_INSTRUCTION}

Relevant excerpts from the paper (may be compressed for length):

{context}

User request: {query}

Provide a concise, accurate summary based only on the excerpts above."""
    llm = ScaleDownLLM()
    return llm.generate(prompt)
