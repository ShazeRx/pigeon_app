from django.urls import path, include

from pigeon.views import index

urlpatterns = [
    path('login/', include('pigeon.auth.login.urls')),
    path('', index)
]
