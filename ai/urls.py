from django.urls import path

from .views import ResumeParseView

urlpatterns = [
    path("parse-resume/", ResumeParseView.as_view(), name="parse-resume"),
]