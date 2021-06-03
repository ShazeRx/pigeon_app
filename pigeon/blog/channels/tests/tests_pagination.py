from django.contrib.auth.models import User
from django.test import TestCase
from model_bakery import baker
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


class ChannelPaginationTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.quantity = 13
        channels = baker.make('pigeon.Channel', _quantity=cls.quantity)
        for channel in channels:
            channel.save()
        cls.user_data = {
            'email': 'some_email',
            'username': 'some_username1',
            'password': 'some_password'
        }
        cls.user = User.objects.create_user(**cls.user_data)
        cls.channels_url = reverse('channels-list')

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_page_should_contain_6_items_by_default(self):
        # when
        response = self.client.get(self.channels_url)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], self.quantity)

    def test_page_should_display_by_query_size_parameter(self):
        # when
        response = self.client.get(f'{self.channels_url}?channel_size=12')
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 12)

    def test_page_should_display_max_13_items(self):
        # when
        response = self.client.get(f'{self.channels_url}?channel_size=14')
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 12)

    def test_response_should_contain_link_to_next_page(self):
        # when
        response = self.client.get(self.channels_url)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['next'], 'http://testserver/channels/?page=2')

    def test_response_should_not_contain_link_to_previous_page(self):
        # when
        response = self.client.get(self.channels_url)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['previous'], None)

    def test_paginator_should_display_second_page(self):
        # when
        response = self.client.get(f'{self.channels_url}?page=2')
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['previous'], 'http://testserver/channels/')
        self.assertEqual(len(response.data['results']), 6)

    def test_should_throw_404_when_page_out_of_range(self):
        # when
        response = self.client.get(f'{self.channels_url}?page=4')
        # then
        self.assertEqual(response.status_code, 404)
