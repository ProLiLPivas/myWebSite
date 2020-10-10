# Generated by Django 2.2.7 on 2020-03-31 12:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True)),
                ('is_online', models.BooleanField(default=True)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='')),
                ('about', models.TextField(blank=True)),
                ('last_online', models.DateTimeField(blank=True)),
                ('posts', models.IntegerField(default=0)),
                ('friends', models.IntegerField(default=0)),
                ('subscribers', models.IntegerField(default=0)),
                ('subscriptions', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
