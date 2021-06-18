from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import *

from pigeon.blog.channels.serializers import ChannelSerializer
from pigeon.blog.posts.pagination import PostPagination
from pigeon.blog.posts.serializers import PostSerializer, GlobalPostSerializer
from pigeon.models import Post, Channel, Image, Like, PostImage


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
            channel_serializer = ChannelSerializer(context={'request': self.request})
            channel = Channel.objects.get(id=self.request.query_params.get('channel'))
            has_access = channel_serializer.get_has_access(channel)
            if not has_access:
                raise ValidationError(
                    detail={"message": f'User {self.request.user} not part of channel with id {channel.id}'},
                    code=403)
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
        images = request.FILES.getlist('images')
        for image in images:
            photo = PostImage.objects.create(image=image, post=serializer.instance)
            photo.save()
        return Response(serializer.data)

    def destroy(self, request: Request, *args, **kwargs):
        post = Post.objects.get(id=kwargs.get('pk'))
        serializer = self.get_serializer(post)
        serializer.remove()
        return Response(status=HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def like(self, request, *args, **kwargs) -> Response:
        user = self.request.user
        post = Post.objects.get(id=kwargs.get('pk'))
        like = Like.objects.filter(user=user, post=post).first()
        if not like:
            like = Like.objects.create(post=post, user=user)
            like.save()
            return Response(status=HTTP_200_OK)
        like.delete()
        return Response(status=HTTP_204_NO_CONTENT)
