from django import forms

from apps.relations.models import Relations
from .models import *


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text', 'is_ancillary']


class ChatForm(forms.ModelForm):
    class Meta:
        model = Relations
        fields = ['user_one']

class ChatSettingsForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = [
            'see_messages',
            'send_messages',
            'del_messages',
            'add_new_users',
            'remove_users',
            'add_remove_admins',
            'see_admins',
            'change_chat_name',
            'change_chat_image',
        ]
