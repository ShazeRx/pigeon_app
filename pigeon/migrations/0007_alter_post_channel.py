# Generated by Django 3.2 on 2021-05-07 09:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pigeon', '0006_auto_20210505_0735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='channel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='pigeon.channel'),
        ),
    ]