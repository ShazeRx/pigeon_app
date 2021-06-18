import tempfile
from unittest import mock
from unittest.mock import patch

from django.contrib.auth.models import User
from model_bakery import baker
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

from pigeon.blog.images.serializers import  PostImageSerializer
from pigeon.blog.posts.serializers import GlobalPostSerializer, PostSerializer
from pigeon.blog.tags.serializers import PostTagSerializer
from pigeon.models import Post, Image, Like, PostImage


class TestPostView(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user_data = {
            'email': 'some_email',
            'username': 'some_username1',
            'password': 'some_password'
        }
        cls.user = User.objects.create_user(**cls.user_data)

    def setUp(self) -> None:
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.client.force_authenticate(self.user)

    def test_should_create_global_post(self):
        # given
        post = baker.make('pigeon.Post')
        serializer_data = GlobalPostSerializer(post).data
        # when
        url = reverse('posts-list')
        response = self.client.post(url, data=serializer_data)
        # then
        self.assertEqual(response.status_code, 200)

    def test_should_remove_global_post_by_author(self):
        # given
        post = baker.make('pigeon.Post', author=self.user)
        # when
        url = reverse('posts-detail', args=[post.id])
        response = self.client.delete(url)
        # then
        self.assertEqual(response.status_code, 200)

    def test_should_retrieve_global_posts(self):
        # given
        posts = baker.make('pigeon.Post', _quantity=5)
        serializer = GlobalPostSerializer(posts, many=True)
        # when
        url = reverse('posts-list')
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], serializer.data)

    def test_should_update_global_post(self):
        # given
        post = baker.make('pigeon.Post', author=self.user)
        new_post_data = baker.prepare('pigeon.Post', author=self.user)
        # when
        serializer_data = GlobalPostSerializer(new_post_data).data
        url = reverse('posts-detail', args=[post.id])
        response = self.client.patch(url, data=serializer_data)
        # then
        self.assertEqual(response.status_code, 200)
        db_post = Post.objects.get(id=post.id)
        self.assertEqual(db_post.title, serializer_data['title'])
        self.assertEqual(db_post.body, serializer_data['body'])

    def test_should_throw_401_when_trying_to_update_global_post_by_not_author(self):
        # given
        post = baker.make('pigeon.Post')
        new_post_data = baker.prepare('pigeon.Post')
        # when
        serializer_data = GlobalPostSerializer(new_post_data).data
        url = reverse('posts-detail', args=[post.id])
        response = self.client.patch(url, data=serializer_data)
        # then
        self.assertEqual(response.status_code, 400)

    def test_should_throw_400_when_remove_global_post_by_not_author(self):
        # given
        post = baker.make('pigeon.Post')
        # when
        url = reverse('posts-detail', args=[post.id])
        response = self.client.delete(url)
        # then
        self.assertEqual(response.status_code, 400)

    def test_should_retrieve_valid_comments_count(self):
        # given
        post = baker.make('pigeon.Post')
        baker.make('pigeon.Comment', post=post, _quantity=5)
        # when
        url = reverse('posts-detail', args=[post.id])
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments_count'], 5)

    def test_should_throw_400_when_trying_to_fetch_private_post(self):
        # given
        channel = baker.make('pigeon.Channel')
        post = baker.make('pigeon.Post', channel=channel)
        # when
        url = reverse('posts-list')
        response = self.client.get(f'{url}?channel={channel.id}')
        # then
        self.assertEqual(response.status_code, 400)

    def test_should_assign_author_from_request(self):
        # given
        post = baker.make('pigeon.Post')
        serializer_data = GlobalPostSerializer(post).data
        # when
        url = reverse('posts-list')
        response = self.client.post(url, data=serializer_data)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['author']['id'], self.user.id)

    @patch('django.db.models.fields.files.FieldFile.url')
    def test_should_return_valid_image_url(self, mock_url):
        # given
        post = baker.make('pigeon.Post')
        image_name = tempfile.NamedTemporaryFile(suffix=".jpg").name
        mock_url.return_value = image_name
        image = baker.make('pigeon.PostImage', post=post, image=image_name)
        image_serializer_data = PostImageSerializer(image).data
        # when
        url = reverse('posts-detail', args=[post.id])
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PostImage.objects.get().image.url, image_serializer_data['image'])

    def test_should_link_tags_correctly(self):
        # given
        post = baker.make('pigeon.Post')
        tags = baker.prepare('pigeon.Tag', _quantity=2)
        post_serializer_data = GlobalPostSerializer(post).data
        tag_serializer_data = PostTagSerializer(tags, many=True)
        post_serializer_data['tags'] = tag_serializer_data.data
        # when
        url = reverse('posts-list')

        response = self.client.post(url, data=post_serializer_data)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['tags']), 2)

    def test_should_throw_401_when_trying_to_update_private_post_by_not_author(self):
        # given
        channel = baker.make('pigeon.Channel', channel_access=[self.user, ])
        post = baker.make('pigeon.Post', channel=channel)
        new_post_data = baker.prepare('pigeon.Post')
        mock_request = self.factory.patch(f'/')
        mock_request.user = self.user
        # when
        with mock.patch('pigeon.blog.channels.serializers.ChannelSerializer.get_has_access', return_value=True):
            serializer_data = PostSerializer(new_post_data, context={"request": mock_request}).data
        url = reverse('posts-detail', args=[post.id])
        response = self.client.patch(f'{url}?channel={channel.id}', data=serializer_data)
        # then
        self.assertEqual(response.status_code, 400)

    def test_should_retrieve_posts_from_private_channel(self):
        # given
        channel = baker.make('pigeon.Channel', owner=self.user)
        posts = baker.make('pigeon.Post', _quantity=5, channel=channel)
        mock_request = self.factory.get(f'/')
        mock_request.user = self.user
        serializer_data = PostSerializer(posts, many=True, context={"request": mock_request}).data
        # when
        url = reverse('posts-list')
        response = self.client.get(f'{url}?channel={channel.id}')
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], serializer_data)

    def test_should_remove_post_from_channel(self):
        # given
        channel = baker.make('pigeon.Channel', channel_access=[self.user, ])
        post = baker.make('pigeon.Post', author=self.user, channel=channel)
        # when
        url = reverse('posts-detail', args=[post.id])
        response = self.client.delete(f'{url}?channel={channel.id}', )
        # then
        self.assertEqual(response.status_code, 200)
        assert Post.objects.count() == 0

    def test_should_remove_post_from_channel_by_channel_owner(self):
        # given
        channel = baker.make('pigeon.Channel', owner=self.user)
        post = baker.make('pigeon.Post', channel=channel)
        # when
        url = reverse('posts-detail', args=[post.id])
        response = self.client.delete(f'{url}?channel={channel.id}', )
        # then
        self.assertEqual(response.status_code, 200)
        assert Post.objects.count() == 0

    def test_should_remove_post_from_channel_by_post_author(self):
        # given
        channel = baker.make('pigeon.Channel', channel_access=[self.user, ])
        post = baker.make('pigeon.Post', channel=channel, author=self.user)
        # when
        url = reverse('posts-detail', args=[post.id])
        response = self.client.delete(f'{url}?channel={channel.id}', )
        # then
        self.assertEqual(response.status_code, 200)
        assert Post.objects.count() == 0

    def test_should_throw_400_when_trying_to_delete_by_author_by_has_no_access_to_channel(self):
        # given
        channel = baker.make('pigeon.Channel')
        post = baker.make('pigeon.Post', channel=channel, author=self.user)
        # when
        url = reverse('posts-detail', args=[post.id])
        response = self.client.delete(f'{url}?channel={channel.id}', )
        # then
        self.assertEqual(response.status_code, 400)
        assert Post.objects.count() == 1

    def test_should_throw_400_when_trying_to_delete_and_not_author(self):
        # given
        channel = baker.make('pigeon.Channel', channel_access=[self.user, ])
        post = baker.make('pigeon.Post', channel=channel)
        # when
        url = reverse('posts-detail', args=[post.id])
        response = self.client.delete(f'{url}?channel={channel.id}', )
        # then
        self.assertEqual(response.status_code, 400)
        assert Post.objects.count() == 1

    def test_should_update_post_from_channel(self):
        # given
        channel = baker.make('pigeon.Channel', channel_access=[self.user, ])
        post = baker.make('pigeon.Post', author=self.user, channel=channel)
        new_post_data = baker.prepare('pigeon.Post')
        mock_request = self.factory.patch(f'/')
        mock_request.user = self.user
        with mock.patch('pigeon.blog.channels.serializers.ChannelSerializer.get_has_access', return_value=True):
            serializer_data = PostSerializer(new_post_data, context={"request": mock_request}).data
        # when
        url = reverse('posts-detail', args=[post.id])
        response = self.client.patch(f'{url}?channel={channel.id}', data=serializer_data)
        # then
        self.assertEqual(response.status_code, 200)
        db_post = Post.objects.get(id=post.id)
        self.assertEqual(db_post.title, serializer_data['title'])
        self.assertEqual(db_post.body, serializer_data['body'])

    def test_should_update_post_from_channel_by_channel_owner(self):
        # given
        channel = baker.make('pigeon.Channel', owner=self.user)
        post = baker.make('pigeon.Post', channel=channel)
        new_post_data = baker.prepare('pigeon.Post')
        mock_request = self.factory.patch(f'/')
        mock_request.user = self.user
        with mock.patch('pigeon.blog.channels.serializers.ChannelSerializer.get_has_access', return_value=True):
            serializer_data = PostSerializer(new_post_data, context={"request": mock_request}).data
        # when
        url = reverse('posts-detail', args=[post.id])
        response = self.client.patch(f'{url}?channel={channel.id}', data=serializer_data)
        # then
        self.assertEqual(response.status_code, 200)
        db_post = Post.objects.get(id=post.id)
        self.assertEqual(db_post.title, serializer_data['title'])
        self.assertEqual(db_post.body, serializer_data['body'])

    def test_should_update_post_from_channel_by_post_author(self):
        # given
        channel = baker.make('pigeon.Channel', channel_access=[self.user, ])
        post = baker.make('pigeon.Post', channel=channel, author=self.user)
        new_post_data = baker.prepare('pigeon.Post')
        mock_request = self.factory.patch(f'/')
        mock_request.user = self.user
        with mock.patch('pigeon.blog.channels.serializers.ChannelSerializer.get_has_access', return_value=True):
            serializer_data = PostSerializer(new_post_data, context={"request": mock_request}).data
        # when
        url = reverse('posts-detail', args=[post.id])
        response = self.client.patch(f'{url}?channel={channel.id}', data=serializer_data)
        # then
        self.assertEqual(response.status_code, 200)
        db_post = Post.objects.get(id=post.id)
        self.assertEqual(db_post.title, serializer_data['title'])
        self.assertEqual(db_post.body, serializer_data['body'])

    def test_should_throw_400_when_trying_to_update_by_author_by_has_no_access_to_channel(self):
        # given
        channel = baker.make('pigeon.Channel')
        post = baker.make('pigeon.Post', channel=channel, author=self.user)
        new_post_data = baker.prepare('pigeon.Post')
        mock_request = self.factory.patch(f'/')
        mock_request.user = self.user
        with mock.patch('pigeon.blog.channels.serializers.ChannelSerializer.get_has_access', return_value=True):
            serializer_data = PostSerializer(new_post_data, context={"request": mock_request}).data
        # when
        url = reverse('posts-detail', args=[post.id])
        response = self.client.patch(f'{url}?channel={channel.id}', data=serializer_data)
        # then
        self.assertEqual(response.status_code, 400)
        assert Post.objects.count() == 1

    def test_should_add_like(self):
        # given
        post = baker.make('pigeon.Post')
        # when
        url = reverse('posts-like', args=[post.id])
        response = self.client.post(url)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Like.objects.count(), 1)
        self.assertEqual(Like.objects.get().post.id, post.id)
        self.assertEqual(Like.objects.get().user.id, self.user.id)

    def test_should_remove_like(self):
        # given
        post = baker.make('pigeon.Post')
        like = baker.make('pigeon.Like', post=post, user=self.user)
        # when
        url = reverse('posts-like', args=[post.id])
        response = self.client.post(url)
        # then
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Like.objects.count(), 0)

    def test_should_return_likes_count(self):
        # given
        post = baker.make('pigeon.Post')
        baker.make('pigeon.Like', post=post, user=self.user)
        # when
        url = reverse('posts-detail', args=[post.id])
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['likes_count'], 1)
