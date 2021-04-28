from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Chat(models.Model):
    PERMISSIONS_TYPES = ((1, 'All Users'), (2, 'Only Admins'),(3, 'Nobody'))

    message_amount = models.IntegerField(default=0)
    user_amount = models.IntegerField(default=0)
    is_public = models.BooleanField(default=False)
    chat_name = models.CharField(
        max_length=150, db_index=True, blank=True, null=True)
    chat_image = models.ImageField(blank=True, null=True)
    last_message_id = models.IntegerField(null=True)
    users = models.ManyToManyField(
        User, related_name='connections', through='ConnectionToChat', blank=True)
    # settings
    send_messages = models.IntegerField(choices=PERMISSIONS_TYPES, default=1)
    del_messages = models.IntegerField(choices=PERMISSIONS_TYPES, default=2)
    add_new_users = models.IntegerField(choices=PERMISSIONS_TYPES, default=1)
    remove_users = models.IntegerField(choices=PERMISSIONS_TYPES, default=2)
    add_remove_admins = models.IntegerField(choices=PERMISSIONS_TYPES, default=3)
    see_admins = models.IntegerField(choices=PERMISSIONS_TYPES, default=1)
    change_chat_name = models.IntegerField(choices=PERMISSIONS_TYPES, default=2)
    change_chat_image = models.IntegerField(choices=PERMISSIONS_TYPES, default=2)

    def get_last_message(self):
        return Message.objects.get(id=self.last_message_id)

    def set_last_message(self, text, is_ancillary=False):
        message = Message.objects.create(
            chat=self, is_ancillary=is_ancillary, text=text, )
        self.last_message_id = message.id
        self.save()

    def save(self, **kwargs):
        if not self.id:
            Message.objects.create(
                chat=self, text='chat was created', is_ancillary=True)
        super().save(**kwargs)




class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    time = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True, db_index=True)
    is_ancillary = models.BooleanField(default=False)
    is_changed = models.BooleanField(default=False)

    def save(self, **kwargs):
        if not self.id:
            super().save(**kwargs)
            self.chat.last_message_id = self.id
            self.chat.save()
        else:
            super().save(**kwargs)

    def delete(self, **kwargs):
        if self.chat.last_message_id == self.id:
            self.chat.last_message_id = \
                Message.objects.filter(chat=self.chat).last().id
            self.chat.save()
        super().delete()

class ConnectionToChat(models.Model):
    """ every user in chat MUST 2 have this column in db """
    ROLES_TYPES = (
        (1, 'simple user'),
        (2, 'administrator'),
        (3, 'creator'),
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='chat_user')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    role = models.IntegerField(choices=ROLES_TYPES, default=1)
    last_seen_message = models.ForeignKey(Message,
        on_delete=models.CASCADE,  null=True, related_name='last_seen_message')

    def get_absolute_url(self):
        if self.chat.is_public:
            return PublicChatConnection.objects.get(id=self.id).get_absolute_url()
        else:
            return PrivateChatConnection.objects.get(id=self.id).get_absolute_url()


class PrivateChatConnection(ConnectionToChat):
    recipient = models.ForeignKey(
        User, null=True, on_delete=models.CASCADE, related_name='recipient')

    def get_absolute_url(self):
        return reverse('private_chat_url', kwargs={'id': self.recipient.id})


class PublicChatConnection(ConnectionToChat):
    chat_num = models.IntegerField(null=True, default=1)

    def get_absolute_url(self):
        return reverse('public_chat_url', kwargs={'id': self.chat_num})

    def save(self, **kwargs):
        if not self.id:
            last_chat = PublicChatConnection.objects.filter(
                user=self.user).order_by('chat_num').last()
            if last_chat:
                self.chat_num = last_chat.chat_num + 1
            else:
                self.chat_num = 1
            text = '{} join chat'.format(self.user)
            Message.objects.create(
                chat=self.chat, text='text', is_ancillary=True)
        super().save(**kwargs)


