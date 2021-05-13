from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from pigeon.blog.posts.pagination import PostPagination
from pigeon.blog.posts.serializers import PostSerializer, GlobalPostSerializer
from pigeon.models import Post


class PostViewSet(viewsets.ModelViewSet):
    """
    View for posts
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    pagination_class = PostPagination

    def get_queryset(self):
        return Post.objects.filter(channel_id=self.kwargs.get('channel_pk')).order_by('created_at')

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

    def get_serializer_context(self):
        context = super(PostViewSet, self).get_serializer_context()
        context.update({'channel_id': self.kwargs.get('channel_pk')})
        return context


class GlobalPostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = GlobalPostSerializer
    pagination_class = PostPagination

    def get_queryset(self):
        return Post.objects.filter(channel_id=None).order_by('created_at')
