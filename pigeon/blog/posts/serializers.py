from django.contrib.auth.models import User
from rest_framework import serializers
from pigeon.auth.serializers import UserSerializer
from pigeon.models import Post


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(many=False, read_only=True)
    """
    class for serializing Post model
    """

    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = ('id', 'created_at')
        write_only = ('image',)

    def to_internal_value(self, data):
        """
        Method for translating author id from request to nested serializer user object
        """
        self.fields['author'] = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
        return super(PostSerializer, self).to_internal_value(data)
