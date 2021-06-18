from pigeon.models import Comment, Post, Tag, Channel, Image, ChannelImage, PostImage
from django.contrib import admin

admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Channel)
admin.site.register(ChannelImage)
admin.site.register(PostImage)
# Register your models here.
