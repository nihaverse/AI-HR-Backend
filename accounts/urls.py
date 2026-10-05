from django.urls import path
from .views import MeView, SignupView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("me/", MeView.as_view(), name="me"),
]