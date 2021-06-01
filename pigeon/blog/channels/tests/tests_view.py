from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from model_bakery import baker
from rest_framework.test import APIClient

from pigeon.blog.channels.serializers import ChannelSerializer
from pigeon.models import Channel


class TestChannelSerializer(TestCase):
    def setUp(self) -> None:
        self.public_channel_data = {
            "name": "test_channel",
            "isPrivate": "False"
        }
        self.user_data = {
            'email': 'some_email',
            'username': 'some_username1',
            'password': 'some_password'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_should_create_channel(self):
        # when
        response = self.client.post('/api/channels/', data=self.public_channel_data)
        # then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Channel.objects.count(), 1)

    def test_should_retrieve_channel_list(self):
        # given
        channels = baker.make('pigeon.Channel', _quantity=2)
        serializer = ChannelSerializer(channels, many=True)
        for channel in channels:
            channel.save()
        # when
        response = self.client.get('/api/channels/')
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], serializer.data)

    def test_should_retrieve_one_channel(self):
        # given
        channel = baker.make('pigeon.Channel', owner=self.user)
        channel.save()
        with mock.patch('pigeon.blog.channels.serializers.ChannelSerializer.get_has_access', return_value=True):
            serializer_data = ChannelSerializer(instance=channel).data
        # when
        response = self.client.get(f'/api/channels/{channel.id}/')
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer_data)

    def test_should_update_channel(self):
        # given
        channel = baker.make('pigeon.Channel', owner=self.user)
        channel.save()
        new_channel_data = baker.make('pigeon.Channel', owner=self.user, id=channel.id)
        with mock.patch('pigeon.blog.channels.serializers.ChannelSerializer.get_has_access', return_value=True):
            serializer_data = ChannelSerializer(new_channel_data).data
        # when
        response = self.client.patch(f'/api/channels/{channel.id}/', data=serializer_data)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer_data)

    def test_should_delete_channel(self):
        # given
        channel = baker.make('pigeon.Channel', owner=self.user)
        channel.save()
        # when
        response = self.client.delete(f'/api/channels/{channel.id}/')
        # then
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Channel.objects.count(), 0)

    def test_channel_should_has_owner_field_assigned_to_creator(self):
        # when
        response = self.client.post('/api/channels/', data=self.public_channel_data)
        # then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['owner']['id'], self.user.id)

    def test_has_access_field_should_be_true_for_creator(self):
        # when
        response = self.client.post('/api/channels/', data=self.public_channel_data)
        # then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['has_access'], True)

    def test_channel_access_should_contain_creator_id(self):
        # when
        response = self.client.post('/api/channels/', data=self.public_channel_data)
        # then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Channel.objects.get().channelAccess.get().id, 1)

    def test_should_add_user_to_channel_to_global_channel(self):
        # given
        channel = baker.make('pigeon.Channel')
        channel.save()
        # when
        response = self.client.post(f'/api/channels/{channel.id}/authenticate/')
        channel.refresh_from_db()
        # then
        self.assertContains(response, 'Authenticated', status_code=200)
        self.assertEqual(channel.channelAccess.get(), self.user)

    def test_should_add_user_to_channel_to_private_channel_with_valid_password(self):
        # given
        password = "123"
        channel = baker.make('pigeon.Channel', password=password, isPrivate=False)
        channel.save()
        # when
        response = self.client.post(f'/api/channels/{channel.id}/authenticate/', data={"password": password})
        channel.refresh_from_db()
        # then
        self.assertContains(response, 'Authenticated', status_code=200)
        self.assertEqual(channel.channelAccess.get(), self.user)

    def test_should_throw_401_when_adding_to__private_channel_with_wrong_password(self):
        # given
        password = "123"
        channel = baker.make('pigeon.Channel', password=password, isPrivate=True)
        channel.save()
        # when
        response = self.client.post(f'/api/channels/{channel.id}/authenticate/', data={"password": 12})
        channel.refresh_from_db()
        # then
        self.assertContains(response, 'Unauthorized', status_code=401)
        self.assertEqual(channel.channelAccess.count(), 0)

    def test_should_remove_from_channel(self):
        # given
        channel = baker.make('pigeon.Channel', channelAccess=[self.user, ])
        channel.save()
        # when
        response = self.client.post(f'/api/channels/{channel.id}/unauthenticate/')
        channel.refresh_from_db()
        # then
        self.assertContains(response, 'Removed', status_code=200)
        self.assertEqual(channel.channelAccess.count(), 0)

    def test_should_generate_new_password_for_channel(self):
        # given
        channel = baker.make('pigeon.Channel')
        channel.save()
        # when
        response = self.client.get(f'/api/channels/{channel.id}/generate_password/')
        channel.refresh_from_db()
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['password'], channel.password)

    def test_generated_password_should_be_16_char_length(self):
        # given
        channel = baker.make('pigeon.Channel')
        channel.save()
        # when
        response = self.client.get(f'/api/channels/{channel.id}/generate_password/')
        channel.refresh_from_db()
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['password']), 16)
