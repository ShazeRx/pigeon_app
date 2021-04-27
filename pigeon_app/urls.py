from django.contrib import admin
from django.urls import include, path
"""
Urls for main django page
"""
urlpatterns = [
    path('api/', include('pigeon.urls')),
    path('admin/', admin.site.urls),
]