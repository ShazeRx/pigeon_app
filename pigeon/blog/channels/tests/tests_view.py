from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from model_bakery import baker
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory

from pigeon.blog.channels.serializers import ChannelSerializer
from pigeon.models import Channel


class TestChannelView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.public_channel_data = {
            "name": "test_channel",
            "isPrivate": "False"
        }
        cls.user_data = {
            'email': 'some_email',
            'username': 'some_username1',
            'password': 'some_password'
        }
        cls.user = User.objects.create_user(**cls.user_data)
        cls.channels_url = reverse('channels-list')

    def setUp(self) -> None:
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.client.force_authenticate(self.user)

    def test_should_create_channel(self):
        # when
        response = self.client.post(self.channels_url, data=self.public_channel_data)
        # then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Channel.objects.count(), 1)

    def test_should_retrieve_channel_list(self):
        # given
        channels = baker.make('pigeon.Channel', _quantity=2)
        mock_request = self.factory.patch(f'/')
        mock_request.user = self.user
        serializer = ChannelSerializer(channels, many=True, context={'request': mock_request})
        for channel in channels:
            channel.save()
        # when
        response = self.client.get(self.channels_url)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], serializer.data)

    def test_should_retrieve_one_channel(self):
        # given
        channel = baker.make('pigeon.Channel', owner=self.user)
        with mock.patch('pigeon.blog.channels.serializers.ChannelSerializer.get_has_access', return_value=True):
            serializer_data = ChannelSerializer(instance=channel).data
        # when
        url = reverse('channels-detail', args=[channel.id, ])
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer_data)

    def test_should_update_channel(self):
        # given
        channel = baker.make('pigeon.Channel', owner=self.user)
        new_channel_data = baker.make('pigeon.Channel', owner=self.user, id=channel.id)
        with mock.patch('pigeon.blog.channels.serializers.ChannelSerializer.get_has_access', return_value=True):
            serializer_data = ChannelSerializer(new_channel_data).data
        # when
        url = reverse('channels-detail', args=[channel.id, ])
        response = self.client.patch(url, data=serializer_data)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer_data)

    def test_should_delete_channel(self):
        # given
        channel = baker.make('pigeon.Channel', owner=self.user)
        # when
        url = reverse('channels-detail', args=[channel.id, ])
        response = self.client.delete(url)
        # then
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Channel.objects.count(), 0)

    def test_channel_should_has_owner_field_assigned_to_creator(self):
        # when
        response = self.client.post(self.channels_url, data=self.public_channel_data)
        # then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['owner']['id'], self.user.id)

    def test_has_access_field_should_be_true_for_creator(self):
        # when
        response = self.client.post(self.channels_url, data=self.public_channel_data)
        # then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['has_access'], True)

    def test_channel_access_should_contain_creator_id(self):
        # when
        response = self.client.post(self.channels_url, data=self.public_channel_data)
        # then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Channel.objects.get().channelAccess.get().id, 1)

    def test_should_add_user_to_channel_to_global_channel(self):
        # given
        channel = baker.make('pigeon.Channel')
        # when
        url = reverse('channels-authenticate', args=[channel.id, ])
        response = self.client.post(url)
        channel.refresh_from_db()
        # then
        self.assertContains(response, 'Authenticated', status_code=200)
        self.assertEqual(channel.channelAccess.get(), self.user)

    def test_should_add_user_to_channel_to_private_channel_with_valid_password(self):
        # given
        password = "123"
        channel = baker.make('pigeon.Channel', password=password, isPrivate=False)
        # when
        url = reverse('channels-authenticate', args=[channel.id, ])
        response = self.client.post(url, data={"password": password})
        channel.refresh_from_db()
        # then
        self.assertContains(response, 'Authenticated', status_code=200)
        self.assertEqual(channel.channelAccess.get(), self.user)

    def test_should_throw_401_when_adding_to_private_channel_with_wrong_password(self):
        # given
        password = "123"
        channel = baker.make('pigeon.Channel', password=password, isPrivate=True)
        # when
        url = reverse('channels-authenticate', args=[channel.id, ])
        response = self.client.post(url, data={"password": 12})
        channel.refresh_from_db()
        # then
        self.assertContains(response, 'Unauthorized', status_code=401)
        self.assertEqual(channel.channelAccess.count(), 0)

    def test_should_remove_from_channel(self):
        # given
        channel = baker.make('pigeon.Channel', channelAccess=[self.user, ])
        # when
        url = reverse('channels-unauthenticate', args=[channel.id, ])
        response = self.client.post(url)
        channel.refresh_from_db()
        # then
        self.assertContains(response, 'Removed', status_code=200)
        self.assertEqual(channel.channelAccess.count(), 0)

    def test_should_generate_new_password_for_channel(self):
        # given
        channel = baker.make('pigeon.Channel')
        # when
        url = reverse('channels-password', args=[channel.id, ])
        response = self.client.get(url)
        channel.refresh_from_db()
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['password'], channel.password)

    def test_generated_password_should_be_16_char_length(self):
        # given
        channel = baker.make('pigeon.Channel')
        # when
        url = reverse('channels-password', args=[channel.id, ])
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['password']), 16)

    def test_should_throw_500_when_channel_does_not_exist(self):
        # given
        url = reverse('channels-detail', args=[1, ])
        # when
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, 500)

    def test_should_401_when_not_part_of_channel_and_trying_to_retrieve(self):
        # given
        channel = baker.make('pigeon.Channel')
        url = reverse('channels-detail', args=[channel.id, ])
        # when
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, 401)
