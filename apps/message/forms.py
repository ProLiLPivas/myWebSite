from django import forms

from apps.relations.models import Relations
from .models import *


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']


class ChatForm(forms.ModelForm):
    class Meta:
        model = Relations
        fields = ['user_one']
