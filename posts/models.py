from time import time
from django.db import models
from django.shortcuts import reverse
from django.utils.text import slugify


def generate_slug(title):
    generated_slug = slugify(title, allow_unicode=True)
    return generated_slug + '_' + str(int(time()))




class Post(models.Model):
    title = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=150, blank=True, unique=True)
    body = models.TextField(blank=True, db_index=True)
    date_publication = models.DateTimeField(auto_now_add=True)
    tag = models.ManyToManyField('Tag', blank=True, related_name='posts')

    def get_absolute_url(self):
        return reverse('read_post_url', kwargs={'slug' : self.slug})

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = generate_slug(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Tag(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, blank=True, unique=True)

    def get_absolute_url(self):
        return reverse('read_tag_url', kwargs={'slug' : self.slug})

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = generate_slug(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title