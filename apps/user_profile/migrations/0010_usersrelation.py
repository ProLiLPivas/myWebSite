# Generated by Django 2.2.7 on 2021-01-13 23:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0009_auto_20201111_1925'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsersRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_friends', models.BooleanField(default=False)),
                ('is_subscribed', models.BooleanField(default=False)),
                ('is_block', models.BooleanField(default=False)),
                ('main_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user1', to='user_profile.Profile')),
                ('related_object', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, to='user_profile.UsersRelation')),
                ('secondary_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user2', to='user_profile.Profile')),
            ],
        ),
    ]