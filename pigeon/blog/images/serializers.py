from rest_framework import serializers

from pigeon.models import Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response.pop("post")
        return response
