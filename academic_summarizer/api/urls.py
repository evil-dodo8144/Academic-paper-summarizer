from django.urls import path
from .views import APIRootView, SummarizePaperView, CompressPaperView

urlpatterns = [
    path('', APIRootView.as_view(), name='api_root'),
    path('summarize/', SummarizePaperView.as_view()),
    path('compress/', CompressPaperView.as_view()),
]
