from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def get_by_username(self, data) -> User:
        username = data['username']
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(f'User {username} does not exist')
