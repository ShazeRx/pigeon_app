from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from pigeon.blog.posts.pagination import PostPagination
from pigeon.blog.posts.serializers import PostSerializer, GlobalPostSerializer
from pigeon.models import Post


class PostViewSet(viewsets.ModelViewSet):
    """
    View for posts
    """
    permission_classes = [IsAuthenticated]
    pagination_class = PostPagination

    def get_serializer_class(self):
        if self.request.query_params.get("channel", ''):
            return PostSerializer
        return GlobalPostSerializer

    def get_queryset(self):
        if self.get_serializer_class() == PostSerializer:
            return Post.objects.filter(channel_id=self.request.query_params.get('channel')).order_by('created_at')
        return Post.objects.filter(channel_id=None).order_by('created_at')

    def list(self, request, *args, **kwargs):
        """
        Get all posts
        """
        posts = self.get_queryset()
        page = self.paginate_queryset(posts)
        serializer = self.get_serializer(page, many=True,
                                         context={
                                             'request': request})
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    def create(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={
            'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request: Request, *args, **kwargs):
        post = Post.objects.get(id=kwargs.get('pk'))
        serializer = self.get_serializer(post)
        serializer.remove()
        return Response(status=HTTP_200_OK)
