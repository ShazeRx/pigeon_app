# Generated by Django 3.2 on 2021-05-05 05:35

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pigeon', '0005_customuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='channelAccess',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]