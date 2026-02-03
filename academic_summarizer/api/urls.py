from django.urls import path
from .views import SummarizePaperView

urlpatterns = [
    path('summarize/', SummarizePaperView.as_view()),
]
