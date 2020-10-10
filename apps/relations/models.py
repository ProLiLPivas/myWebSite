from django.db import models
from django.urls import reverse

from apps.user_profile.models import Profile


class Relations(models.Model):

    user_one = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='user1')
    user_two = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='user2')
    is_friends = models.BooleanField(default=False)
    is_subscribed = models.BooleanField(default=False)
    is_block = models.BooleanField(default=False)

    def get_private_chat_url(self):
        return reverse('private_chat_url', kwargs={'id': self.user_two.id})



