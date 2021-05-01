from django.contrib.auth.models import User
from django.test import TestCase
from pigeon.auth.serializers import UserSerializer


class UserSerializerTest(TestCase):
    def setUp(self) -> None:
        self.user_data = {
            'email': 'some_email',
            'username': 'some_username1',
            'password': 'some_password'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.serializer = UserSerializer(instance=self.user)

    def test_returns_token_after_creating_user(self):
        data = self.serializer.data
        self.assertIn('tokens', data.keys())
        self.assertIsNotNone(data.get('tokens')['refresh'] and data.get('tokens')['access'])

    def test_get_username_by_name_should_return_user_instance(self):
        self.assertIsInstance(self.serializer.get_by_username({'username': self.user_data.get('username')}), User)

    def test_get_username_by_name_should_return_valid_user(self):
        user_data_without_password = dict(self.user_data)
        user_data_without_password.pop('password')
        assert (user_data_without_password.items() <= self.serializer.get_by_username(
            {'username': self.user_data.get('username')}).__dict__.items())

    def test_get_token_should_return_pair_token(self):
        self.assertEqual(len(self.serializer.get_token(self.user).items()), 2)
