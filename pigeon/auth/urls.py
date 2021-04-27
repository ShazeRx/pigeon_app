from django.urls import path

from pigeon.auth.views import RegisterView, LoginView
"""
Urls for authentication
"""
urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
]
