from pigeon.blog.comments.views import CommentViewSet
from pigeon.blog.posts.views import PostViewSet
from rest_framework_nested import routers

"""
Urls for authentication
"""

router = routers.SimpleRouter()
router.register(r'', PostViewSet, basename='posts', )

comment_router = routers.NestedSimpleRouter(router, r'', lookup='post')
comment_router.register(r'comments', CommentViewSet, basename='post-comments')

urlpatterns = router.urls + comment_router.urls
