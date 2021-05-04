from django.contrib.auth.models import User
from rest_framework import serializers
from pigeon.auth.serializers import UserSerializer
from pigeon.blog.posts.serializers import PostSerializer
from pigeon.models import Comment, Post


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    post = PostSerializer(many=False, read_only=True)

    class Meta:
        fields = "__all__"
        read_only_fields = ('id', 'created_at')
        model = Comment

    def to_internal_value(self, data):
        """
        Method for translating user id and post id from request to nested serializer user, post object
        """
        if 'post_id' in self.context:
            data['post'] = self.context['post_id']
        """Set nested fields to primary related when data being serialized into object"""
        self.fields['user'] = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
        self.fields['post'] = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
        return super(CommentSerializer, self).to_internal_value(data)

    def to_representation(self, instance):
        """
        Method for returning Post JSON with nested user field without tokens
        """
        response = super().to_representation(instance)
        response['user'] = UserSerializer(instance.user).data
        if 'tokens' in response['user']:
            response['user'].pop('tokens')
        response.pop("post")
        return response
