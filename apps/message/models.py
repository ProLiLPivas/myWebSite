from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse



class Chat(models.Model):
    PERMISSIONS_TYPES = ((1, 'All Users'), (2, 'Only Admins'),(3, 'Nobody'))

    message_amount = models.IntegerField(default=0)
    user_amount = models.IntegerField(default=0)
    is_public = models.BooleanField(default=False)
    chat_name = models.CharField(max_length=150, db_index=True, blank=True, null=True)
    chat_image = models.ImageField(blank=True, null=True)
    last_message_id = models.IntegerField(null=True)
    # settings
    see_messages = models.IntegerField(choices=PERMISSIONS_TYPES, default=1)
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

    def create_last_message(self, text):
        first_message = Message.objects.create(chat=self, is_ancillary=True, text=text, )
        self.last_message_id = first_message.id
        self.save()

class Connection2Chat(models.Model):
    """ every user in chat MUST 2 have this column in db """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='recipient') # using to get recipient in private chats
    chat_num = models.IntegerField(null=True)  # using to generate url for public chat
    role = models.IntegerField(default=1) # 1 - simple user, 2 - admin, 3 - creator

    def get_chat_url(self):
        if self.chat.is_public:
            return reverse('public_chat_url', kwargs={'id': self.chat_num})
        else:
            return reverse('private_chat_url', kwargs={'id': self.recipient.id})



class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    time = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True, db_index=True)
    is_seen = models.BooleanField(default=False)
    is_ancillary = models.BooleanField(default=False)
    is_changed = models.BooleanField(default=False)