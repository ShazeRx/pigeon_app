from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
"""
Urls for main django page
"""
urlpatterns = [
    path('api/', include('pigeon.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)