from django.urls import path, include

from pigeon.views import index

urlpatterns = [
    path('auth/', include('pigeon.auth.urls')),
    path('', index)
]
