from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import *

from pigeon.blog.channels.pagination import ChannelPagination
from pigeon.blog.channels.serializers import ChannelSerializer
from pigeon.blog.utils.utils import BlogSerializerUtils
from pigeon.models import Channel


class ChannelViewSet(viewsets.ModelViewSet):
    """
    View for posts
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChannelSerializer
    pagination_class = ChannelPagination

    def get_queryset(self):
        return Channel.objects.filter(is_private=False).order_by('id')

    def create(self, request: Request, *args, **kwargs):
        """
        Create channel
        """
        serializer = self.get_serializer(data=request.data, context={
            'request': request})
        serializer.is_valid(raise_exception=True)
        images = request.FILES.getlist('image')
        if not len(images) > 1:
            serializer.save()
            for image in images:
                serializer.save_image(image, serializer.instance)
            return Response(serializer.data)
        return Response(data={'message': 'Channel can have only one image'}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def authenticate(self, request, *args, **kwargs) -> Response:
        """
        Add user to channel, if channel isPrivate parameter is True then
        password query parameter need to be added to request with valid password
        :return:
        """
        password = request.query_params.get('password', '')
        channel = Channel.objects.filter(is_private=True, password=password).first()
        if channel:
            channel.channel_access.add(request.user)
            channel.save()
            return Response(data={'message': 'Authenticated'})
        return Response(data={'message': 'Unauthorized'}, status=HTTP_401_UNAUTHORIZED)

    @action(detail=True, methods=['post'])
    def unauthenticate(self, request, *args, **kwargs) -> Response:
        """
        Remove user from channel
        """
        channel_pk = kwargs.get('pk', '')
        serializer = ChannelSerializer()
        channel = serializer.get_channel_by_id(channel_pk)
        channel.channel_access.remove(request.user)
        channel.save()
        return Response(data={'message': 'Removed'})

    @action(detail=False, methods=['get'])
    def has_access(self, request, *args, **kwargs):
        queryset = Channel.objects.filter(channel_access__in=[self.request.user]).order_by('id')
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True,
                                         context={
                                             'request': request})
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """
        Retrieve channel by id
        """
        id = kwargs.get('pk')
        try:
            channel = Channel.objects.get(id=id)
        except Channel.DoesNotExist:
            return Response(data={'message': f'Channel not found with id {id}'}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = ChannelSerializer(channel, context={'request': request})
        if serializer.get_has_access(channel):
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(data={'message': f'User {request.user} not part of channel with id {id}'},
                        status=HTTP_401_UNAUTHORIZED)

    @action(detail=True, methods=['get'])
    def password(self, request, *args, **kwargs) -> Response:
        """
        Generate random password for channel
        """
        channel = Channel.objects.get(id=kwargs['pk'])
        channel.password = BlogSerializerUtils.randomize_password(Channel.objects.all())
        channel.save()
        return Response(data={'password': channel.password})
