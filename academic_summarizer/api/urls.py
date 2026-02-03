from django.urls import path
from .views import APIRootView, SummarizePaperView

urlpatterns = [
    path('', APIRootView.as_view(), name='api_root'),
    path('summarize/', SummarizePaperView.as_view()),
]
