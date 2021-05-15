from django.contrib.auth.models import User
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.relations import PrimaryKeyRelatedField
from pigeon.auth.serializers import UserSerializer
from pigeon.blog.tags.serializers import ChannelTagSerializer
from pigeon.models import Channel, Tag, Post


class ChannelSerializer(WritableNestedModelSerializer):
    channelAccess = PrimaryKeyRelatedField(many=True, write_only=True, queryset=User.objects.all(), required=False)
    has_access = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    owner = UserSerializer(many=False, read_only=True, allow_null=False)
    number_of_members = serializers.SerializerMethodField()
    number_of_posts = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = "__all__"
        read_only_fields = ("id",)  # this field works veird, i've spent 2 hours of debugging it
        extra_kwargs = {'password': {'write_only': True}}

    def to_internal_value(self, data: dict):
        """
        Method for translating author id from request to nested serializer user object
        """
        user_id = self.context['request'].user.id
        data.update({'owner': user_id})
        self.fields['owner'] = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
        return super(ChannelSerializer, self).to_internal_value(data)

    def get_has_access(self, channel: Channel) -> bool:
        request = self.context.get('request', None)
        if request:
            user = request.user
            return user in channel.channelAccess.all()
        return False

    def get_number_of_members(self, channel: Channel) -> int:
        return channel.channelAccess.count()

    def get_number_of_posts(self, channel: Channel) -> int:
        return Post.objects.filter(channel=channel.id).count()

    def get_channel_by_id(self, id: int) -> Channel:
        return get_object_or_404(Channel, id=id)

    def get_tags(self, channel: Channel):
        tags = Tag.objects.filter(channel=channel.id)
        serializer = ChannelTagSerializer(tags, many=True)
        return serializer.data

    def check_password_equals(self, data: dict, obj: Channel) -> bool:
        """
        Method for checking if password from request matching obj password
        :param data: json/dict in format
        {
        'password':'any_password'
        }
        :param obj: Post object to which to password will be compared
        :return: True if passwords match, else return response in following format:
        {
            "message": "Wrong post password was provided"
        }
        with code 403
        """
        password = '' if 'password' not in data else data['password']
        if obj.isPrivate and password != obj.password:
            err = serializers.ValidationError({'message': "Wrong post password was provided"})
            err.status_code = 403
            raise err
        return True

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        channel = Channel(**validated_data)
        channel.save()
        channel.channelAccess.add(user_id)
        channel.password = User.objects.make_random_password()
        return channel
