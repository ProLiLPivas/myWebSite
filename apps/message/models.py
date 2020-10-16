from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.urls import reverse



class Chat(models.Model):
    message_amount = models.IntegerField(default=0)
    user_amount = models.IntegerField(default=2)
    is_public = models.BooleanField(default=False)
    chat_name = models.CharField(max_length=150, db_index=True, blank=True, null=True)
    chat_image = models.ImageField(blank=True, null=True)
    last_message_id = models.IntegerField(null=True)
    # settings
    # send_messages
    # del_messages
    #
    #


    def get_last_message(self):
        return Message.objects.get(id=self.last_message_id)


class Connection2Chat(models.Model):
    """ every user in chat MUST 2 have this column in db """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    chat_id = models.ForeignKey(Chat, on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='recipient') # using to get recipient in private chats
    chat_num = models.IntegerField(null=True)  # using to generate url for public chat
    # role  = models.IntegerField(default=0), # 0 - simple user, 1 - admin, 3 - creator

    def get_chat_url(self):
        if self.chat_id.is_public:
            return reverse('public_chat_url', kwargs={'id': self.chat_num})
        else:
            return reverse('private_chat_url', kwargs={'id': self.recipient.id})

class Message(models.Model):
    chat_id = models.ForeignKey(Chat, on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True, db_index=True)
    is_seen = models.BooleanField(default=False)