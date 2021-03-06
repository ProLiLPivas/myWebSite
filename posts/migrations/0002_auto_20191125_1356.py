# Generated by Django 2.2.7 on 2019-11-25 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('slug', models.SlugField(max_length=150, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='tag',
            field=models.ManyToManyField(blank=True, related_name='posts', to='posts.Tag'),
        ),
    ]
