from django.contrib.auth.models import User
from model_bakery import baker
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

from pigeon.blog.comments.serializers import CommentSerializer
from pigeon.models import Comment


class TestCommentView(APITestCase):
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

    def setUp(self) -> None:
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.client.force_authenticate(self.user)

    def test_should_display_comments(self):
        # given
        post = baker.make('pigeon.Post')
        comments = baker.make('pigeon.Comment', _quantity=2, post=post)
        comment_serializer_data = CommentSerializer(comments, many=True).data
        # when
        url = reverse('post-comments-list', args=[post.id, ])
        response = self.client.get(url)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], comment_serializer_data)

    def test_should_remove_comment_by_author(self):
        # given
        post = baker.make('pigeon.Post')
        comment = baker.make('pigeon.Comment', post=post, user=self.user)
        # when
        url = reverse('post-comments-detail', args=[post.id, comment.id])
        response = self.client.delete(url)
        # then
        self.assertEqual(response.status_code, 200)
        assert Comment.objects.count() == 0

    def test_should_update_comment_by_author(self):
        # given
        post = baker.make('pigeon.Post')
        comment = baker.make('pigeon.Comment', post=post, user=self.user)
        new_comment_data = baker.prepare('pigeon.Comment')
        comment_serializer_data = CommentSerializer(new_comment_data).data
        # when
        url = reverse('post-comments-detail', args=[post.id, comment.id])
        response = self.client.patch(url, data=comment_serializer_data)
        # then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.get().body, comment_serializer_data['body'])

    def test_should_throw_400_when_delete_by_not_author(self):
        # given
        post = baker.make('pigeon.Post')
        comment = baker.make('pigeon.Comment', post=post)
        # when
        url = reverse('post-comments-detail', args=[post.id, comment.id])
        response = self.client.delete(url)
        # then
        self.assertEqual(response.status_code, 400)
        assert Comment.objects.count() == 1

    def test_should_throw_400_when_update_by_not_author(self):
        # given
        post = baker.make('pigeon.Post')
        comment = baker.make('pigeon.Comment', post=post)
        new_comment_data = baker.prepare('pigeon.Comment')
        comment_serializer_data = CommentSerializer(new_comment_data).data
        # when
        url = reverse('post-comments-detail', args=[post.id, comment.id])
        response = self.client.patch(url, data=comment_serializer_data)
        # then
        self.assertEqual(response.status_code, 400)
        self.assertNotEqual(Comment.objects.get().body, comment_serializer_data['body'])

    def test_should_throw_401_when_trying_to_access_comments_and_not_part_of_channel(self):
        # given
        channel = baker.make('pigeon.Channel')
        post = baker.make('pigeon.Post', channel=channel)
        baker.make('pigeon.Comment', post=post)
        # when
        url = reverse('post-comments-list', args=[post.id, ])
        response = self.client.get(f'{url}?channel={channel.id}')
        # then
        self.assertEqual(response.status_code, 400)
