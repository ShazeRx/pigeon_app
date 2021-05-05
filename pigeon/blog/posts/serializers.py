import re
from django.contrib.auth.models import User
from rest_framework import serializers
from pigeon.auth.serializers import UserSerializer
from pigeon.models import Post


class PostSerializer(serializers.ModelSerializer):
    # TODO: implement https://github.com/beda-software/drf-writable-nested library
    author = UserSerializer(many=False, read_only=True)
    """
    class for serializing Post model
    """

    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = ('id', 'created_at')
        write_only = ('image',)
        extra_kwargs = {'password': {'write_only': True}}

    def check_password_equals(self, data: dict, obj: Post) -> bool:
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

    def validate_password(self, value: str):
        """
        Method checks if password is valid with regex
        :param value: password that need to be checked
        """
        if not re.match("^[$&+,:;=?@#|'<>.^*()%!a-zA-Z0-9]{4,}", value) and bool(self.initial_data['isPrivate']):
            raise serializers.ValidationError({'message': 'Password is not secure'})
        return value

    def to_internal_value(self, data):
        """
        Method for translating author id from request to nested serializer user object
        """
        self.fields['author'] = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
        return super(PostSerializer, self).to_internal_value(data)

    def to_representation(self, instance):
        """
        Method for returning Post JSON with nested author field without tokens
        """
        response = super().to_representation(instance)
        response['author'] = UserSerializer(instance.author).data
        response['author'].pop('tokens')
        return response
