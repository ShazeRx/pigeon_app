from rest_framework_nested import routers

from pigeon.blog.comments.views import  CommentViewSet
from pigeon.blog.posts.views import PostViewSet

post_router = routers.SimpleRouter()
post_router.register(r'', PostViewSet, basename='posts')

comment_router = routers.NestedSimpleRouter(post_router, r'', lookup='post')
comment_router.register(r'comments', CommentViewSet, basename='post-comments')

urlpatterns = post_router.urls + comment_router.urls
