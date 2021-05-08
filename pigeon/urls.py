from django.urls import path, include

from pigeon.views import index
"""
Urls for pigeon app
"""
urlpatterns = [
    path('auth/', include('pigeon.auth.urls')),
    path('posts/', include('pigeon.blog.posts.urls')),
    path('channels/', include('pigeon.blog.urls')),
    path('', index)
]
