from rest_framework import routers

from pigeon.blog.posts.views import PostViewSet

"""
Urls for authentication
"""

router = routers.SimpleRouter()
router.register(r'', PostViewSet)
urlpatterns = router.urls
