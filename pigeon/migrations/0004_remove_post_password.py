# Generated by Django 3.2 on 2021-05-05 04:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pigeon', '0003_auto_20210505_0620'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='password',
        ),
    ]
