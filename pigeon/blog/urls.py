from pigeon.blog.channels.views import ChannelViewSet
from pigeon.blog.comments.views import CommentViewSet
from pigeon.blog.posts.views import PostViewSet
from rest_framework_nested import routers

"""
Urls for authentication
"""
channel_router = routers.SimpleRouter()
channel_router.register(r'', ChannelViewSet, basename='channels')

post_router = routers.NestedSimpleRouter(channel_router, r'', lookup='channel')
post_router.register(r'posts', PostViewSet, basename='posts', )

comment_router = routers.NestedSimpleRouter(post_router, r'posts', lookup='post')
comment_router.register(r'comments', CommentViewSet, basename='post-comments')

urlpatterns = channel_router.urls + post_router.urls + comment_router.urls
