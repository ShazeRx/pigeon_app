from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

class UserSerializer(serializers.ModelSerializer):
    tokens = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'username', 'tokens']
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'], 
            password=validated_data['password']
        )
        return user

    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return tokens

    def get_by_username(self, data) -> User:
        username = data['username']
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(f'User {username} does not exist')








