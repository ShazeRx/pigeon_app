from django.contrib.auth.models import User
from django.test import TestCase
from pigeon.auth.serializers import UserSerializer
from rest_framework.exceptions import ValidationError


class UserSerializerTest(TestCase):
    def setUp(self) -> None:
        self.user_data = {
            'email': 'some_email',
            'username': 'some_username1',
            'password': 'some_password'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.serializer = UserSerializer(instance=self.user)

    def test_get_username_by_name_should_return_user_instance(self):
        self.assertIsInstance(self.serializer.get_by_username({'username': self.user_data.get('username')}), User)

    def test_get_username_by_name_should_return_valid_user(self):
        user_data_without_password = dict(self.user_data)
        user_data_without_password.pop('password')
        assert (user_data_without_password.items() <= self.serializer.get_by_username(
            {'username': self.user_data.get('username')}).__dict__.items())

    def test_get_token_should_return_pair_token(self):
        self.assertEqual(len(self.serializer.get_token(self.user).items()), 2)

    def test_get_none_existing_user_should_throw_exception(self):
        self.assertRaises(ValidationError, self.serializer.get_by_username, {'username': 'non_exist'})

    def test_create_should_return_user_instance(self):
        user_data = {
            'email': 'some@email.pl',
            'username': 'some_username2',
            'password': 'some_password1'
        }
        serializer = UserSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.assertEqual(serializer.validated_data, user_data)
