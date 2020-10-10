from django import forms

from apps.relations.models import Relations
from .models import *


class MessageForm(forms.ModelForm):

    class Meta:

        model = Message
        fields = ['text']

        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'})
        }

class ChatForm(forms.ModelForm):

    class Meta:

        model = Relations
        fields = ['user_one']

        # fields.field_classes


        widgets = {
             'user_one': forms.CheckboxInput(attrs={'class': 'form-control'}),

        }