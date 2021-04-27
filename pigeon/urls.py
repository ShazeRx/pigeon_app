from django.urls import path, include

from pigeon.views import index
"""
Urls for pigeon app
"""
urlpatterns = [
    path('auth/', include('pigeon.auth.urls')),
    path('', index)
]
