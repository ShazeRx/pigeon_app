from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import AbstractUser


class Channel(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    password = models.CharField(max_length=128, null=True, blank=True)
    isPrivate = models.BooleanField(null=False)
    channelAccess = models.ManyToManyField(User)
    owner = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='channel_owner')


class Post(models.Model):
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    title = models.CharField(max_length=50)
    channel = models.ForeignKey(Channel, null=True, blank=True, on_delete=models.SET_NULL)


class Tag(models.Model):
    name = models.CharField(max_length=100, null=False)
    post = models.ManyToManyField(Post)
    channel = models.ManyToManyField(Channel)


class Comment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
