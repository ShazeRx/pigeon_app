from django.contrib.auth.models import User
from rest_framework import serializers

from pigeon.auth.serializers import UserSerializer
from pigeon.blog.tags.serializers import PostTagSerializer
from pigeon.models import Post, Channel, Tag, Comment


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(many=False, read_only=True)
    tags = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
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
        user_id = self.context['request'].user.id
        channel_id = self.context['channel_id']
        data.update({'author': user_id})
        data.update({'channel': channel_id})
        self.fields['channel'] = serializers.PrimaryKeyRelatedField(queryset=Channel.objects.all(), allow_null=True)
        self.fields['author'] = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
        return super(PostSerializer, self).to_internal_value(data)

    def to_representation(self, instance: Post):
        user = self.context['request'].user
        has_access = user in instance.channel.channelAccess.all()
        if has_access:
            return super(PostSerializer, self).to_representation(instance)
        raise serializers.ValidationError(
            detail={"message": f'User {user} not part of channel with id {instance.channel.id}'},
            code=403)

    def get_tags(self, post: Post):
        return Tag.objects.filter(id=post.id)

    def get_comments_count(self, post: Post):
        return Comment.objects.filter(post=post.id)


class GlobalPostSerializer(serializers.ModelSerializer):
    author = UserSerializer(many=False, read_only=True)
    tags = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    """
    class for serializing Post model
    """

    class Meta:
        model = Post
        exclude = ['channel']
        read_only_fields = ('id', 'created_at')
        write_only = ('image',)

    def get_tags(self, post: Post):
        tags = Tag.objects.filter(post=post.id)
        serializer = PostTagSerializer(tags, many=True)
        return serializer.data

    def get_comments_count(self, post: Post):
        return Comment.objects.filter(post=post.id).count()
