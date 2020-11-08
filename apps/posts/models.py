from time import time
from django.db import models
from django.shortcuts import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User


def generate_slug(title):
    generated_slug = slugify(title, allow_unicode=True)
    return generated_slug + '_' + str(int(time()))


class Post(models.Model):
    title = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=150, blank=True, unique=True)
    body = models.TextField(blank=True, db_index=True)
    date_publication = models.DateTimeField(auto_now_add=True)
    tag = models.ManyToManyField('Tag', blank=True, related_name='posts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, default='1')
    likes_amount = models.IntegerField(default=0)
    comments_amount = models.IntegerField(default=0)
    reposts_amount = models.IntegerField(default=0)
    # is_changed = models.BooleanField(default=False, null=True)

    def get_absolute_url(self):
        return reverse('read_post_url', kwargs={'slug': self.id})

    def get_comments_url(self):
        return reverse('comment_url', kwargs={'id': self.id})

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = generate_slug(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date_publication']


class Tag(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, blank=True)


    def get_absolute_url(self):
        return reverse('read_tag_url', kwargs={'slug' : self.title})

    def get_related_posts(self):
        return #self.

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = self.title
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE,)
    text = models.TextField()
    time = models.TimeField(auto_now_add=True)
    likes_amount = models.IntegerField(default=0)

    class Meta:
        ordering = ['-time']


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default='1')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    exist = models.BooleanField(default=False)

