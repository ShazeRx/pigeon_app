from .views import LoginView, RegisterView, VerifyEmailView
from django.urls import path
"""
Urls for authentication
"""
urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('email-verify/', VerifyEmailView.as_view(), name='email-verify'),
]
