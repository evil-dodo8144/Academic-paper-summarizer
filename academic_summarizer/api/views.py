import tempfile

from django.views.generic import View
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from rag.summarize import summarize_pdf, compress_pdf


class APIRootView(View):
    """API root: product description and endpoints."""

    def get(self, request):
        return JsonResponse({
            "message": "Academic Paper Summarizer",
            "description": "Research paper summarization using RAG and compression for lengthy papers, preserving technical accuracy and reducing processing time.",
            "endpoints": {
                "summarize": "/api/summarize/ (POST: file, query)",
            },
        })


class SummarizePaperView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        pdf = request.FILES.get("file")
        query = request.data.get("query", "Summarize this paper")
        if not pdf:
            return Response({"error": "No file provided"}, status=400)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            for chunk in pdf.chunks():
                tmp.write(chunk)
            file_path = tmp.name

        result = summarize_pdf(file_path, query)
        return Response({"summary": result})


class CompressPaperView(APIView):
    """
    API endpoint to return a compressed representation of the PDF text using
    the ScaleDown compress API (configured via SCALEDOWN_API_KEY and
    SCALEDOWN_COMPRESS_URL).
    """

    parser_classes = [MultiPartParser]

    def post(self, request):
        pdf = request.FILES.get("file")
        context = request.data.get("context", "Full academic paper text to compress.")

        if not pdf:
            return Response({"error": "No file provided"}, status=400)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            for chunk in pdf.chunks():
                tmp.write(chunk)
            file_path = tmp.name

        compressed = compress_pdf(file_path, context=context)
        return Response({"compressed": compressed})
