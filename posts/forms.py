from django import forms
from django.core.exceptions import ValidationError

from .models import *


class TagForm(forms.Form):
    title = forms.CharField(max_length=150)
    slug = forms.CharField(max_length=150)

    title.widget.attrs.update({'class':'form-control'})
    slug.widget.attrs.update({'class': 'form-control'})


    def clean_slug(self):
        new_slug = self.cleaned_data.get('slug').lower()
        if new_slug == 'create':
            raise ValidationError('slug may not be "create"')
        return new_slug


    def save(self):
        new_tag = Tag.objects.create(
            title=self.cleaned_data.get('title'),
            slug=self.cleaned_data.get('slug')
        )
        return new_tag
