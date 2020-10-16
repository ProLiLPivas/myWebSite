from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=50, default='')
    is_online = models.BooleanField(default=True)
    avatar = models.ImageField(blank=True, null=True)
    about = models.TextField(blank=True,)

    posts = models.IntegerField(default=0)
    friends = models.IntegerField(default=0)
    subscribers = models.IntegerField(default=0)
    subscriptions = models.IntegerField(default=0)

    # 1 -> all , 2 -> only subscribers, 3 -> only friends, 4 -> nobody ,  5 is only for u
    access_messaging = models.IntegerField(default=1)
    access_add_friends = models.IntegerField(default=1)
    access_post = models.IntegerField(default=1)
    access_about = models.IntegerField(default=1)
    access_albums = models.IntegerField(default=1)
    access_images = models.IntegerField(default=1)
    access_stats = models.IntegerField(default=1)
    access_profile = models.IntegerField(default=1)


    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        self.slug = 'id{}'.format(self.user_id)
        super().save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse('get_user_url', kwargs={'slug' : self.slug})

    def get_chat_url(self):
        return reverse('private_chat_url', kwargs={'id': self.user.id})

    def subscribe_url(self):
        return reverse('subscribe', kwargs={'slug': self.slug})

    def add_friend_url(self):
        return reverse('add_friend', kwargs={'slug': self.slug})

    def unsubscribe_url(self):
        return reverse('unsubscribe', kwargs={'slug': self.slug})

    def remove_friend_url(self):
        return reverse('remove_friend', kwargs={'slug': self.slug})



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()



# class Relations(models.Model):
#
#     user_one = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='user1')
#     user_two = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='user2')
#     is_friends = models.BooleanField(default=False)
#     is_subscribed = models.BooleanField(default=False)
#     is_block = models.BooleanField(default=False)
#
#     def get_private_chat_url(self):
#         return reverse('private_chat_url', kwargs={'id': self.user_two.id})
