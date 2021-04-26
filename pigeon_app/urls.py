from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('api/', include('pigeon.urls')),
    path('admin/', admin.site.urls),
]