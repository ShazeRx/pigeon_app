# Generated by Django 3.2 on 2021-06-11 04:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pigeon', '0016_like'),
    ]

    operations = [
        migrations.RenameField(
            model_name='channel',
            old_name='channelAccess',
            new_name='channel_access',
        ),
        migrations.RenameField(
            model_name='channel',
            old_name='isPrivate',
            new_name='is_private',
        ),
    ]