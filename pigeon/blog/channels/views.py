from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import *

from pigeon.blog.channels.pagination import ChannelPagination
from pigeon.blog.channels.serializers import ChannelSerializer
from pigeon.models import Channel


class ChannelViewSet(viewsets.ModelViewSet):
    """
    View for posts
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChannelSerializer
    pagination_class = ChannelPagination

    def get_queryset(self):
        return Channel.objects.all().order_by('id')

    @action(detail=True, methods=['post'])
    def authenticate(self, request, *args, **kwargs) -> Response:
        """
        Add user to channel, if channel isPrivate parameter is True then
        password query parameter need to be added to request with valid password
        :return:
        """
        channel_pk = kwargs.get('pk', '')
        serializer = ChannelSerializer()
        channel = serializer.get_channel_by_id(channel_pk)
        password = request.query_params.get('password', '')
        is_valid_password = channel.password is None if password == '' else password
        if is_valid_password or not channel.isPrivate:
            channel.channelAccess.add(request.user)
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
        channel.channelAccess.remove(request.user)
        channel.save()
        return Response(data={'message': 'Removed'})

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
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
        channel.password = User.objects.make_random_password(16)
        channel.save()
        return Response(data={'password': channel.password})
