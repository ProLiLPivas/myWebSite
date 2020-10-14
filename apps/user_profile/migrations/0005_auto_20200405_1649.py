# Generated by Django 2.2.7 on 2020-04-05 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0004_auto_20200331_1656'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='access_about',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='access_friends',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='access_profile',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='access_subscribers',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='access_subscriptions',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, default='', null=True, upload_to=''),
        ),
    ]