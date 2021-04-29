from rest_framework import serializers

from pigeon.models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = ('id', 'created_at', 'author_id')
        write_only = ('image',)
