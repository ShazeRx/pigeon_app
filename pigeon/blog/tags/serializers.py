from drf_writable_nested import WritableNestedModelSerializer
from rest_framework.relations import PrimaryKeyRelatedField

from pigeon.models import Tag, Post, Channel


class PostTagSerializer(WritableNestedModelSerializer):
    post = PrimaryKeyRelatedField(many=True, queryset=Post.objects.all(), write_only=True)

    class Meta:
        model = Tag
        exclude = ['channel', ]
        read_only_fields = ('id',)


class ChannelTagSerializer(WritableNestedModelSerializer):
    channel  = PrimaryKeyRelatedField(many=True, queryset=Channel.objects.all(), write_only=True)

    class Meta:
        model = Tag
        exclude = ['post', ]
        read_only_fields = ('id',)
