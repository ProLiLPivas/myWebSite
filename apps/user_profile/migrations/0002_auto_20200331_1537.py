# Generated by Django 2.2.7 on 2020-03-31 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='last_online',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
