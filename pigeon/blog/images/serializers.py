from rest_framework import serializers

from pigeon.models import ChannelImage, PostImage


class ChannelImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelImage
        fields = "__all__"


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = "__all__"
