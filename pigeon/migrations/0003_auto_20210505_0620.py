# Generated by Django 3.2 on 2021-05-05 04:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('pigeon', '0002_auto_20210426_0751'),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('password', models.CharField(blank=True, max_length=128, null=True)),
                ('isPrivate', models.BooleanField()),
            ],
        ),
        migrations.RemoveField(
            model_name='post',
            name='isPrivate',
        ),
        migrations.AddField(
            model_name='post',
            name='channel',
            field=models.ForeignKey(default=None, blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    to='pigeon.channel'),
            preserve_default=False,
        ),
    ]
