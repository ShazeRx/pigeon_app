from rest_framework.routers import SimpleRouter

from pigeon.blog.posts.views import GlobalPostViewSet

router = SimpleRouter()
router.register(r'', GlobalPostViewSet, basename='global_posts')
urlpatterns = router.urls
