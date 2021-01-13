from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse


class Profile(models.Model):
    # 1 -> all , 2 -> only subscribers, 3 -> only friends, 4 -> nobody ,  5 is only for u
    PERMISSIONS_TYPES = ((1, 'All Users'), (2, 'Only Subscribers'), (3, 'Only Friends'), (4, 'Nobody'))

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=50, default='')
    is_online = models.BooleanField(default=True)
    avatar = models.ImageField(blank=True, null=True)
    about = models.TextField(blank=True,)
    posts = models.IntegerField(default=0)
    friends = models.IntegerField(default=0)
    subscribers = models.IntegerField(default=0)
    subscriptions = models.IntegerField(default=0)

    access_messaging = models.IntegerField(choices=PERMISSIONS_TYPES, default=1)
    access_add_friends = models.IntegerField(choices=PERMISSIONS_TYPES, default=1)
    access_post = models.IntegerField(choices=PERMISSIONS_TYPES, default=1)
    access_about = models.IntegerField(choices=PERMISSIONS_TYPES, default=1)
    access_albums = models.IntegerField(choices=PERMISSIONS_TYPES, default=1)
    access_images = models.IntegerField(choices=PERMISSIONS_TYPES, default=1)
    access_stats = models.IntegerField(choices=PERMISSIONS_TYPES, default=1)
    access_profile = models.IntegerField(choices=PERMISSIONS_TYPES, default=1)

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


class UsersRelation(models.Model):
    main_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='user1')
    secondary_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='user2')
    is_friends = models.BooleanField(default=False)
    is_subscribed = models.BooleanField(default=False)
    is_block = models.BooleanField(default=False)
    related_object = models.OneToOneField('self', on_delete=models.CASCADE, blank=True)

    def get_private_chat_url(self):
        return reverse('private_chat_url', kwargs={'id': self.secondary_user.id})


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
