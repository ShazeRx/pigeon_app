from django.contrib.auth.models import User
from rest_framework import serializers, status

from pigeon.auth.serializers import UserSerializer
from pigeon.blog.channels.serializers import ChannelSerializer
from pigeon.blog.images.serializers import PostImageSerializer
from pigeon.blog.utils.utils import BlogSerializerUtils
from pigeon.blog.tags.serializers import PostTagSerializer
from pigeon.models import Post, Channel, Tag, Comment, Like


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(many=False, read_only=True)
    tags = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    post_images = PostImageSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    """
    class for serializing Post model
    """

    class Meta:
        model = Post
        fields = ["id", "body", "title", "author", "channel", "post_images", "created_at", "tags", "comments_count",
                  "likes_count"]
        read_only_fields = ('id', 'created_at')

    def to_internal_value(self, data):
        """
        Method for translating author id from request to nested serializer user object
        """
        user_id = self.context['request'].user.id
        channel_id = self.context['request'].query_params['channel']
        data.update({'author': user_id})
        data.update({'channel': channel_id})
        self.fields['channel'] = serializers.PrimaryKeyRelatedField(queryset=Channel.objects.all(), allow_null=True)
        self.fields['author'] = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
        return super(PostSerializer, self).to_internal_value(data)

    def get_user_from_request(self):
        return self.context['request'].user

    def to_representation(self, instance: Post):
        user = self.get_user_from_request()
        channel_serializer = ChannelSerializer(context={'request': self.context['request']})
        self.fields['author'] = UserSerializer(many=False, read_only=True, allow_null=False)
        has_access = channel_serializer.get_has_access(instance.channel)
        if has_access:
            return super(PostSerializer, self).to_representation(instance)
        raise serializers.ValidationError(
            detail={"message": f'User {user} not part of channel with id {instance.channel.id}'},
            code=403)

    def create(self, validated_data):
        post = super(PostSerializer, self).create(validated_data)
        if 'tags' in self.context['request'].data:
            tag_list_data = self.context['request'].data['tags']
            tags = [Tag(**tag_data) for tag_data in tag_list_data]
            self.link_tags(post, tags)
        return post

    def get_tags(self, post: Post):
        tags = Tag.objects.filter(post=post.id)
        serializer = PostTagSerializer(tags, many=True)
        return serializer.data

    def get_comments_count(self, post: Post):
        return Comment.objects.filter(post=post.id).count()

    def get_likes_count(self, post: Post):
        return Like.objects.filter(post=post.id).count()

    def validate(self, attrs):
        author = attrs['author']
        channel = attrs.get('channel')
        request_user = self.get_user_from_request()
        if channel is not None and author not in channel.channel_access.all() and request_user != channel.owner:
            raise serializers.ValidationError(detail=f'User {author} not part of channel with id {channel.id}')
        return attrs

    def remove(self):
        user = self.context['request'].user
        post = self.instance
        post_channel = post.channel
        if user == post.author \
                and user in post_channel.channel_access.all() \
                or user == post_channel.owner:
            return post.delete()
        raise serializers.ValidationError(detail=f'User {user} not part of channel with id {post_channel.id}')

    def update(self, instance, validated_data):
        user = self.context['request'].user
        post_channel = instance.channel
        if user == instance.author \
                and user in post_channel.channel_access.all() \
                or user == post_channel.owner:
            tag_list_data = self.context['request'].data['tags']
            tags = [Tag(**tag_data) for tag_data in tag_list_data]
            post_tags = Tag.objects.filter(post=instance.id)
            for tag in post_tags:
                if tag not in tags:
                    tag = Tag.objects.get(id=tag.id)
                    tag.post.remove(instance)
            self.link_tags(instance, tags)
            return super(PostSerializer, self).update(instance, validated_data)
        raise serializers.ValidationError(detail=f'User {user} not part of channel with id {post_channel.id}')

    def link_tags(self, post: Post, tags_to_be_added: list):
        # get all tags which have same names as in request
        existing_tags = Tag.objects.filter(name__in=[tag.name for tag in tags_to_be_added])
        for tag in tags_to_be_added:
            existing_tag = existing_tags.filter(name=tag.name).first()
            if not existing_tag:
                existing_tag = tag
                existing_tag.save()
            existing_tag.post.add(post.id)


class GlobalPostSerializer(PostSerializer):
    """
    class for serializing Global Post model
    """

    class Meta:
        model = Post
        fields = ["id", "body", "title", "author", "post_images", "created_at", "tags", "comments_count", "likes_count"]

    def to_internal_value(self, data):
        """
        Method for translating author id from request to nested serializer user object
        """
        user_id = self.context['request'].user.id
        modified_data = BlogSerializerUtils.add_values_to_dict(data, author=user_id)
        self.fields['author'] = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
        return super(PostSerializer, self).to_internal_value(modified_data)

    def to_representation(self, instance: Post):
        self.fields['author'] = UserSerializer(many=False, read_only=True, allow_null=False)
        return super(PostSerializer, self).to_representation(instance)

    def remove(self):
        user = self.context['request'].user
        post = self.instance
        if user == post.author:
            return post.delete()
        raise serializers.ValidationError(detail=f'User {user} not autor of post with id {post.id}',
                                          code=status.HTTP_401_UNAUTHORIZED)

    def update(self, instance: Post, validated_data):
        user = self.context['request'].user
        if user == instance.author:
            tag_list_data = self.context['request'].data['tags']
            request_tags = [Tag(**tag_data) for tag_data in tag_list_data]
            post_tags = Tag.objects.filter(post=instance.id)
            for tag in post_tags:
                if tag not in request_tags:
                    tag = Tag.objects.get(id=tag.id)
                    tag.post.remove(instance)
            self.link_tags(instance, request_tags)
            return super(PostSerializer, self).update(instance, validated_data)
        raise serializers.ValidationError(detail=f'User {user} not autor of post with id {instance.id}',
                                          code=status.HTTP_401_UNAUTHORIZED)
