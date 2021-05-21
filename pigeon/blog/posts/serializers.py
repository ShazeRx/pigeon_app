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
        channel_id = self.context['request'].query_params['channel']
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

    def create(self, validated_data):
        post = super(PostSerializer, self).create(validated_data)
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

    def validate(self, attrs):
        author = attrs['author']
        channel = attrs.get('channel')
        if channel is not None and author not in channel.channelAccess.all():
            raise serializers.ValidationError(detail=f'User {author} not part of channel with id {channel.id}')
        return attrs

    def remove(self):
        user = self.context['request'].user
        post = self.instance
        post_channel = post.channel
        if user == post.author \
                and user in post_channel.channelAccess.all() \
                or user == post_channel.owner:
            return post.delete()
        raise serializers.ValidationError(detail=f'User {user} not part of channel with id {post_channel.id}')

    def update(self, instance, validated_data):
        user = self.context['request'].user
        post_channel = instance.channel
        if user == instance.author \
                and user in post_channel.channelAccess.all() \
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
        exclude = ['channel']

    def to_internal_value(self, data):
        """
        Method for translating author id from request to nested serializer user object
        """
        user_id = self.context['request'].user.id
        data.update({'author': user_id})
        self.fields['author'] = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
        return super(PostSerializer, self).to_internal_value(data)

    def to_representation(self, instance: Post):
        return super(PostSerializer, self).to_representation(instance)

    def remove(self):
        user = self.context['request'].user
        post = self.instance
        if user == post.author:
            return post.delete()
        raise serializers.ValidationError(detail=f'User {user} not autor of post with id {post.id}')

    def update(self, instance: Post, validated_data):
        user = self.context['request'].user
        if user == instance.author:
            tag_list_data = self.context['request'].data['tags']
            tags = [Tag(**tag_data) for tag_data in tag_list_data]
            post_tags = Tag.objects.filter(post=instance.id)
            for tag in post_tags:
                if tag not in tags:
                    tag = Tag.objects.get(id=tag.id)
                    tag.post.remove(instance)
            self.link_tags(instance, tags)
            return super(PostSerializer, self).update(instance, validated_data)
        raise serializers.ValidationError(detail=f'User {user} not autor of post with id {instance.id}')
