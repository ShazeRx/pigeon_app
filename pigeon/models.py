from django.contrib.auth.models import User
from django.db import models


class Post(models.Model):
    body = models.TextField()
    password = models.CharField(max_length=128)
    isPublic = models.BooleanField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    image = models.ImageField(upload_to='images/')
    title = models.CharField(max_length=50)


class Tag(models.Model):
    name = models.CharField(max_length=100, null=False)
    post = models.ManyToManyField(Post)


class Comment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

