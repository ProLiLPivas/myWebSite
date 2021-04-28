from django import forms

from .models import *


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text', 'is_ancillary', 'chat', 'from_user']


class MessageUpdateForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']
        

class ChatSettingsForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = [
            # 'see_messages',
            # 'send_messages',
            'del_messages',
            'add_new_users',
            'remove_users',
            'add_remove_admins',
            'see_admins',
            'change_chat_name',
            'change_chat_image',
        ]
