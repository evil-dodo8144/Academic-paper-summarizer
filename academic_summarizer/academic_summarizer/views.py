"""Project-level views: landing page and web summarization tool."""

import os
import tempfile

from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render


class HomeView(TemplateView):
    template_name = "home.html"


class SummarizeToolView(View):
    """Web UI: upload PDF + optional query, show summary."""

    def get(self, request):
        return render(request, "summarize.html")

    def post(self, request):
        from rag.summarize import summarize_pdf

        pdf = request.FILES.get("file")
        query = (request.POST.get("query") or "Summarize this paper").strip() or "Summarize this paper"

        if not pdf or not pdf.name.lower().endswith(".pdf"):
            return render(request, "summarize.html", {"error": "Please upload a PDF file."})

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                for chunk in pdf.chunks():
                    tmp.write(chunk)
                file_path = tmp.name
            try:
                summary = summarize_pdf(file_path, query)
                return render(request, "summarize.html", {"summary": summary})
            finally:
                try:
                    os.unlink(file_path)
                except OSError:
                    pass
        except Exception as e:
            return render(request, "summarize.html", {"error": str(e)})
