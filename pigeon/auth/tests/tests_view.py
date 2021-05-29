from django.contrib.auth.models import User
from django.test import TestCase


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
