from rest_framework_nested import routers

from pigeon.blog.channels.views import ChannelViewSet

"""
Urls for authentication
"""
channel_router = routers.SimpleRouter()
channel_router.register(r'', ChannelViewSet, basename='channels')

urlpatterns = channel_router.urls
