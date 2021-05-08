from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.relations import PrimaryKeyRelatedField
from pigeon.auth.serializers import UserSerializer
from pigeon.models import Channel


class ChannelSerializer(serializers.ModelSerializer):
    channelAccess = PrimaryKeyRelatedField(many=True, write_only=True, queryset=User.objects.all(), required=False)
    has_access = serializers.SerializerMethodField()
    owner = UserSerializer(many=False, read_only=True, allow_null=False)

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

    def get_channel_by_id(self, id: int) -> Channel:
        return get_object_or_404(Channel, id=id)
