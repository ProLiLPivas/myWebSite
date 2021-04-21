from time import time
from typing import Dict

from django.db import models
from django.shortcuts import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User

from apps.user_profile.models import UsersRelation


def generate_slug(title):
    generated_slug = slugify(title, allow_unicode=True)
    return generated_slug + '_' + str(int(time()))


class Post(models.Model):
    """

    """
    PERMISSIONS_TYPES = (
        (0, 'All Users'),
        (2, 'Only Subscribers'),
        (4, 'Only Friends'),
        (5, 'Nobody')
    )

    title = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=150, blank=True, unique=True)
    body = models.TextField(blank=True, db_index=True)
    date_publication = models.DateTimeField(auto_now_add=True)
    tag = models.ManyToManyField('Tag', blank=True, related_name='posts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, default='1')
    likes_amount = models.IntegerField(default=0)
    comments_amount = models.IntegerField(default=0)
    reposts_amount = models.IntegerField(default=0)
    is_changed = models.BooleanField(default=False)

    default_permission_settings = {'choices': PERMISSIONS_TYPES, 'default': 0}
    #
    see_comments_permission = models.IntegerField(**default_permission_settings)
    comment_permission = models.IntegerField(**default_permission_settings)
    like_permission = models.IntegerField(**default_permission_settings)
    repost_permission = models.IntegerField(**default_permission_settings)
    see_statistic_permission = models.IntegerField(**default_permission_settings)
    see_author_permission = models.IntegerField(**default_permission_settings)
    see_post_permission = models.IntegerField(**default_permission_settings)


    def get_absolute_url(self):
        return reverse('read_post_url', kwargs={'slug': self.id})

    def get_comments_url(self):
        return reverse('comment_url', kwargs={'id': self.id})

    def get_get_relations_status(self, user: User) -> int:
        return UsersRelation.objects.get_or_create(
            main_user_profile=self.user.profile,
            secondary_user_profile=user.profile
        ).get_relations_status()

    def get_permissions_dict(self, user) -> Dict[str, bool]:
        permission = self.get_get_relations_status(user)
        return {
            'see_profile_permission':  True,
            'see_post_permission': self.see_post_permission <= permission,
            'see_author_permission': self.see_author_permission <= permission,
            'see_statistic_permission': self.see_statistic_permission <= permission,
            'like_permission': self.like_permission <= permission,
            'comment_permission': self.comment_permission <= permission,
            'repost_permission': self.repost_permission <= permission,
        }

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
    # user = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('read_tag_url', kwargs={'slug' : self.title})

    def length(self):
        return len(Post.objects.filter(tag__id=self.id))

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
    is_changed = models.BooleanField(default=False)


    class Meta:
        ordering = ['-time']


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default='1')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    exist = models.BooleanField(default=False)

