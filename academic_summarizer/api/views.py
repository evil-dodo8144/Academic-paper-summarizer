from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from rag.pdf_loader import load_pdf
from rag.chunker import chunk_text
from rag.compressor import compress_chunks
from rag.embeddings import get_embeddings
from rag.vector_store import build_vectorstore
from rag.retriever import get_retriever
from llm.scaledown_client import ScaleDownLLM

import tempfile

class SummarizePaperView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        pdf = request.FILES.get("file")
        query = request.data.get("query", "Summarize this paper")

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            for chunk in pdf.chunks():
                tmp.write(chunk)
            file_path = tmp.name

        text = load_pdf(file_path)
        chunks = chunk_text(text)
        compressed = compress_chunks(chunks)

        embeddings = get_embeddings()
        vectorstore = build_vectorstore(compressed, embeddings)
        retriever = get_retriever(vectorstore)

        docs = retriever.get_relevant_documents(query)
        context = "\n".join(d.page_content for d in docs)

        llm = ScaleDownLLM()
        result = llm.generate(context)

        return Response({"summary": result})
