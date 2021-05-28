from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User class
    """

    # tokens = serializers.SerializerMethodField(
    #     method_name='get_token')  # token is fetched dynamically from get_token method while User is being fetched

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'username']
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True}, 'email': {'required': True}}

    """
        Dispatches a signal before saving an user object into a database.  
        :param pre_save: Signal sent before a model gets saved.
        :param sender=User: Specifies a particular sender to receive signals from.
        """

    @receiver(pre_save, sender=User)
    def set_new_user_inactive(sender, instance, **kwargs):
        if instance._state.adding is True:
            instance.is_active = False
            instance.password = make_password(instance.password)

    def validate(self, data):
        """
        Validates the registration of a new user
        :param data: dict in format
        {
            'email': 'some_email',
            'password': 'some_password',
            'username':'some_username'
        }
        :return: Data if valid, othwerwise raises a validation exception.
        """
        if len(data['email']) == 0:
            raise serializers.ValidationError('Email is required.')
        if User.objects.filter(email=data['email']):
            raise serializers.ValidationError('A user with that email already exists.')
        return data

    def create(self, validated_data: dict) -> User:
        """
        Creates a new user
        :param validated_data: Data to create user (email,username,password) in following format
        {
        'email':'some email',
        'username':'some username',
        'password':'some password',
        }
        :return: created User if was created successfully
        """
        return User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )

    def get_token(self, user: User) -> dict[str, str]:
        """
        Returns new pair of tokens (refresh,access)
        :param user: Object of user for whom token has to be got
        :return: Pair of tokens (refresh,access)
        """
        refresh = UserToken.get_token(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def get_by_username(self, data: dict) -> User:
        """
        Returns object of user by username
        :param data: dict in format
        {
        'username':'some_username'
        }
        :return: Object of user if user has been found, else it raise an ValidationError
        """
        username = data['username']
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(f'User {username} does not exist')


class UserToken(TokenObtainPairSerializer):
    """
    Class for customizing default JWT token
    """

    @classmethod
    def get_token(cls, user: User) -> RefreshToken:
        """
        :rtype: dict[str, str]
        :param user: Object of user for whom token has to be got
        :return: Pair of customized tokens (refresh,access)
        {
            "token_type": "token_type",
            "exp": 9_digit_expiration_time,
            "jti": "secret_jti",
            "user_id": user_id,
            "username": "username",
            "first_name": "first_name",
            "last_name": "last_name",
            "email": "email",
        }
        """
        token = super().get_token(user)
        token['username'] = user.username
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['email'] = user.email
        return token
