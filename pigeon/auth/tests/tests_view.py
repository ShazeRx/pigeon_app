import datetime
import os
import jwt
from django.contrib.auth.models import User
from django.test import TestCase
from pigeon.auth.serializers import UserSerializer
from unittest import mock


class TestLoginView(TestCase):
    def setUp(self) -> None:
        self.data = {
            "username": "hello",
            "password": "world",
            "email": "email"
        }
        User.objects.create_user(**self.data)

    def test_can_login_with_valid_data(self):
        # given
        body = {
            "username": self.data["username"],
            "password": self.data["password"]
        }
        # when
        response = self.client.post("/api/auth/login/", data=body, content_type="application/json")
        # then
        self.assertEqual(response.status_code, 200)

    def test_should_throw_403_when_user_not_exist(self):
        # given
        body = {
            "username": "some",
            "password": "body"
        }
        # when
        response = self.client.post("/api/auth/login/", data=body, content_type="application/json")
        # then
        self.assertEqual(response.status_code, 403)

    def test_should_throw_403_when_body_is_empty(self):
        # given
        body = {
            "username": "",
            "password": ""
        }
        # when
        response = self.client.post("/api/auth/login/", data=body, content_type="application/json")
        # then
        self.assertEqual(response.status_code, 403)


class TestRegisterView(TestCase):
    def setUp(self) -> None:
        self.data = {
            "username": "hello",
            "password": "world",
            "email": "email@email.com"
        }

    def test_should_register_successfully(self):
        # when
        response = self.client.post('/api/auth/register/', data=self.data, content_type="application/json")
        # then
        self.assertEqual(response.status_code, 201)

    def test_should_throw_400_when_empty_username(self):
        # given
        data = {
            "username": "",
            "password": "world",
            "email": "email@email.com"
        }
        # when
        response = self.client.post('/api/auth/register/', data=data, content_type="application/json")
        # then
        self.assertEqual(response.status_code, 400)

    def test_should_throw_400_when_empty_password(self):
        # given
        data = {
            "username": "hello1",
            "password": "",
            "email": "email@email.com"
        }
        # when
        response = self.client.post('/api/auth/register/', data=data, content_type="application/json")
        # then
        self.assertEqual(response.status_code, 400)

    def test_should_throw_400_when_email_is_not_valid(self):
        # given
        data = {
            "username": "hello1",
            "password": "world",
            "email": "emailemail.com"
        }
        # when
        response = self.client.post('/api/auth/register/', data=data, content_type="application/json")
        # then
        self.assertEqual(response.status_code, 400)

    def test_should_throw_400_when_email_is_empty(self):
        # given
        data = {
            "username": "hello1",
            "password": "world",
            "email": ""
        }
        # when
        response = self.client.post('/api/auth/register/', data=data, content_type="application/json")
        # then
        self.assertEqual(response.status_code, 400)

    def test_should_throw_400_when_email_exist(self):
        # given
        user1_data = {
            "username": "hello1",
            "password": "world",
            "email": "email@email.com"
        }
        user2_data = {
            "username": "hello2",
            "password": "world",
            "email": "email@email.com"
        }
        # when
        self.client.post('/api/auth/register/', data=user1_data, content_type="application/json")
        # and
        response = self.client.post('/api/auth/register/', data=user2_data, content_type="application/json")
        # then
        self.assertEqual(response.status_code, 400)

    def test_should_return_token_set(self):
        # when
        response = self.client.post('/api/auth/register/', data=self.data, content_type="application/json")
        # then
        self.assertEqual(len(response.data['tokens']), 2)

    def test_should_return_valid_tokens_pairs(self):
        # when
        response = self.client.post('/api/auth/register/', data=self.data, content_type="application/json")
        # then
        self.assertNotEqual(response.json()['tokens']['access'], "" and response.json()['tokens']['refresh'], "")


class TestVerifyEmailView(TestCase):
    def setUp(self) -> None:
        self.data = {
            "username": "hello",
            "password": "world",
            "email": "email",
            "is_active": False
        }
        self.user = User.objects.create_user(**self.data)
        self.serializer = UserSerializer()
        self.token = self.serializer.get_token(self.user)['access']

    def test_should_activate_user(self):
        # when
        response = self.client.get(f'/api/auth/email-verify/?token={self.token}')
        # then
        self.user.refresh_from_db()
        self.assertContains(response, 'Successfully activated', status_code=200)
        self.assertEqual(self.user.is_active, True)

    @mock.patch.dict(os.environ, {"SECRET_KEY": "secret1"})
    def test_should_throw_invalid_token_error_when_bad_sign(self):
        # when
        response = self.client.get(f'/api/auth/email-verify/?token={self.token}')
        # then
        self.user.refresh_from_db()
        self.assertContains(response, "Invalid token", status_code=400)
        self.assertEqual(self.user.is_active, False)

    def test_should_throw_activation_expired_when_jwt_expired(self):
        # given
        token = self.token
        payload = jwt.decode(jwt=token, key=os.environ.get('SECRET_KEY'), algorithms=['HS256'])
        payload['exp'] = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        token = jwt.encode(payload=payload, key=os.environ.get('SECRET_KEY'), algorithm='HS256')
        # when
        response = self.client.get(f'/api/auth/email-verify/?token={token}')
        # then
        self.user.refresh_from_db()
        self.assertEqual(self.user.is_active, False)
        self.assertContains(response, 'Activation Expired', status_code=400)
