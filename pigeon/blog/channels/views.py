from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import *

from pigeon.blog.channels.serializers import ChannelSerializer
from pigeon.models import Channel


class ChannelViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin,
                     mixins.DestroyModelMixin):
    """
    View for posts
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChannelSerializer

    def get_queryset(self):
        return Channel.objects.all()

    @action(detail=True, methods=['post'])
    def authenticate(self, request, *args, **kwargs):
        channel_pk = kwargs.get('pk', '')
        serializer = ChannelSerializer()
        channel = serializer.get_channel_by_id(channel_pk)
        password = request.query_params.get('password', '')
        is_valid_password = channel.password == password
        if is_valid_password or not channel.isPrivate:
            channel.channelAccess.add(request.user)
            channel.save()
            return Response(data={'message': 'Authenticated'})
        return Response(data={'message': 'Unauthorized'}, status=HTTP_401_UNAUTHORIZED)

    @action(detail=True, methods=['post'])
    def unauthenticate(self, request, *args, **kwargs):
        channel_pk = kwargs.get('pk', '')
        serializer = ChannelSerializer()
        channel = serializer.get_channel_by_id(channel_pk)
        channel.channelAccess.remove(request.user)
        channel.save()
        return Response(data={'message': 'Removed'})
