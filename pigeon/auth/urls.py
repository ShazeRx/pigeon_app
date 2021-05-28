from .views import LoginView, RegisterView, VerifyEmailView
from django.urls import path

from pigeon.auth.views import RegisterView, LoginView
from rest_framework_simplejwt import views as jwt_views

"""
Urls for authentication
"""
urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('refresh/', jwt_views.TokenRefreshView.as_view(), name='toke_refresh')
    path('email-verify/', VerifyEmailView.as_view(), name='email-verify'),
]
