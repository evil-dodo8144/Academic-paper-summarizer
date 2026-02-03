"""Shared RAG + LLM pipeline for summarizing a PDF."""

from rag.pdf_loader import load_pdf
from rag.chunker import chunk_text
from rag.compressor import compress_chunks
from rag.embeddings import get_embeddings
from rag.vector_store import build_vectorstore
from rag.retriever import get_retriever
from llm.scaledown_client import ScaleDownLLM


def summarize_pdf(file_path: str, query: str = "Summarize this paper") -> str:
    """Extract text from PDF, run RAG (chunk → compress → embed → retrieve), then generate summary."""
    text = load_pdf(file_path)
    chunks = chunk_text(text)
    compressed = compress_chunks(chunks)
    embeddings = get_embeddings()
    vectorstore = build_vectorstore(compressed, embeddings)
    retriever = get_retriever(vectorstore)
    docs = retriever.get_relevant_documents(query)
    context = "\n".join(d.page_content for d in docs)
    llm = ScaleDownLLM()
    return llm.generate(context)
