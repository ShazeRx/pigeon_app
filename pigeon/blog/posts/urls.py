from rest_framework_nested import routers

from pigeon.blog.comments.views import GlobalCommentViewSet
from pigeon.blog.posts.views import GlobalPostViewSet

router = routers.SimpleRouter()
router.register(r'', GlobalPostViewSet, basename='global_posts')

comment_router = routers.NestedSimpleRouter(router, r'', lookup='post')
comment_router.register(r'comments', GlobalCommentViewSet, basename='post-comments')
urlpatterns = router.urls + comment_router.urls
