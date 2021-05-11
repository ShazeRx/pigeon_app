from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from pigeon.blog.posts.serializers import PostSerializer, GlobalPostSerializer
from pigeon.models import Post


class PostViewSet(viewsets.ModelViewSet):
    """
    View for posts
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(channel_id=self.kwargs.get('channel_pk'))

    def list(self, request, *args, **kwargs):
        """
        Get all posts
        """
        posts = self.get_queryset()
        serializer = PostSerializer(posts, many=True,
                                    context={
                                        'request': request})  # request context need to be passed to return reversed URL of image
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = PostSerializer(data=request.data, context={
            'request': request, 'channel_id': self.kwargs.get('channel_pk')})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class GlobalPostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = GlobalPostSerializer

    def get_queryset(self):
        return Post.objects.filter(channel_id=None)
