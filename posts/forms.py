from django import forms
from django.core.exceptions import *

from .models import *


class TagForm(forms.Form):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150)

    def clean_slug(self):
        new_slug = self.claeand_data.get('slug').lower()
        if new_slug == 'create':
            raise VaildationError('slug may not be "create"')
        return new_slug


    def save(self):
        new_tag = Tag.objects.create(
            title=self.claeand_data.get('title'),
            slug=self.claeand_data.get('slug')
        )
        return new_tag
