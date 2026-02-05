import { NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get("file") as File | null
    const query = (formData.get("query") as string) || "Summarize this paper"

    if (!file) {
      return NextResponse.json({ error: "No file provided" }, { status: 400 })
    }

    if (!file.name.endsWith(".pdf")) {
      return NextResponse.json({ error: "File must be a PDF" }, { status: 400 })
    }

    // For demo purposes, return a placeholder summary
    // In production, this would connect to your Django backend API or implement the RAG pipeline
    const summary = `This is a demo summary for "${file.name}".

To enable full summarization functionality, you'll need to:

1. Deploy the Django backend (academic_summarizer) with your API keys configured
2. Update this API route to forward requests to your backend at /api/summarize/
3. Or implement the RAG pipeline directly in this Next.js app using:
   - PDF parsing (pdf-parse or similar)
   - Text chunking
   - Embeddings (OpenAI, sentence-transformers via API)
   - Vector store (Pinecone, Supabase, or in-memory)
   - LLM summarization

Query submitted: "${query}"

The original Django application provides:
- PDF text extraction using PyMuPDF
- Paragraph-aware chunking with overlap
- Optional compression via ScaleDown API
- FAISS vector store for retrieval
- LLM-based summarization preserving technical accuracy`

    return NextResponse.json({ summary })
  } catch (error) {
    console.error("Summarization error:", error)
    return NextResponse.json(
      { error: "Failed to process the document" },
      { status: 500 }
    )
  }
}
