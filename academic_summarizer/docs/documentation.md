# Academic Paper Summarizer

A research paper summarization tool that uses **compression** to handle lengthy academic papers while **preserving technical accuracy** and **reducing processing time**.

## What it does

- **Upload a PDF** (research paper, article) and get a concise, accurate summary.
- **RAG (Retrieval-Augmented Generation)**: chunks the document, optionally compresses chunks, embeds them, and retrieves the most relevant parts for your query before generating the summary.
- **Compression**: long documents are chunked and can be compressed (via ScaleDown API or LLM) so that embedding and retrieval stay fast and within context limits.
- **Technical accuracy**: the summarization prompt instructs the model to preserve key terms, methods, and findings.

## Pipeline

1. **Load PDF** → extract text (PyMuPDF).
2. **Chunk** → split into overlapping segments (paragraph-aware, tuned for academic text).
3. **Compress** (optional) → shorten chunks via ScaleDown compress API or an LLM to reduce tokens while keeping meaning.
4. **Embed** → compute embeddings (e.g. sentence-transformers).
5. **Vector store** → FAISS index over compressed chunks.
6. **Retrieve** → fetch top-k chunks most relevant to the user’s query.
7. **Summarize** → LLM generates a summary from the retrieved context, with instructions to preserve technical accuracy.

## Used

**pdf_loader.load_pdf** → extracts text from PDF.
**chunker.chunk_text** → splits text into chunks.
**compressor.compress_chunks** → uses scaledown_compress.compress_text only if SCALEDOWN_COMPRESS_URL is set, otherwise returns original chunks.
**embeddings, vector_store, retriever** → build FAISS retriever.
