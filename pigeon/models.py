from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models


class Channel(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    password = models.CharField(max_length=128, null=True, blank=True)
    is_private = models.BooleanField(null=False)
    channel_access = models.ManyToManyField(User)
    owner = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='channel_owner')

    def __str__(self):
        return f"{self.name}"


class Post(models.Model):
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=50)
    channel = models.ForeignKey(Channel, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.id}:{self.title}, {self.author}"


class Tag(models.Model):
    name = models.CharField(max_length=100, null=False)
    post = models.ManyToManyField(Post, blank=True)
    channel = models.ManyToManyField(Channel, blank=True)

    def __str__(self):
        return f"{self.name}"


class Comment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.body[:10]}, {self.user}"


class Image(models.Model):
    image = models.ImageField(upload_to='images/', null=False, blank=False)

    class Meta:
        abstract = True


class PostImage(Image):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_image")


class ChannelImage(Image):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="channel_image")


class Like(models.Model):
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=False, blank=False, on_delete=models.CASCADE)
