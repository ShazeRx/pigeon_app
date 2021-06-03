from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from pigeon.auth.serializers import UserSerializer
from pigeon.blog.posts.serializers import PostSerializer, GlobalPostSerializer
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
        user_id = self.context['request'].user.id
        post_id = self.context['post_id']
        data.update({'user': user_id})
        data.update({'post': post_id})
        self.fields['user'] = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
        self.fields['post'] = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
        return super(CommentSerializer, self).to_internal_value(data)

    def to_representation(self, instance: Comment):
        """
        Method for returning Post JSON with nested user field without tokens
        """
        if instance.post.channel is None:
            self.fields['post'] = GlobalPostSerializer(many=False, read_only=True)
        response = super().to_representation(instance)
        response.pop("post")
        return response

    def remove(self):
        user = self.context['request'].user
        comment = self.instance
        if user == comment.user:
            return comment.delete()
        raise ValidationError(detail={'message': f'User {user} not author of comment'})

    def update(self, instance, validated_data):
        user = self.context['request'].user
        comment = self.instance
        if user == comment.user:
            return super(CommentSerializer, self).update(instance, validated_data)
        raise ValidationError(detail={'message': f'User {user} not author of comment'})
