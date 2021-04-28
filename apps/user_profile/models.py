from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse


class Profile(models.Model):

    PERMISSIONS_TYPES = (
        (0, 'All Users'),
        (2, 'Only Subscribers'),
        (4, 'Only Friends'),
        (5, 'Nobody')
    )
    default_permission_settings = {'choices': PERMISSIONS_TYPES, 'default': 0}

    user = models.OneToOneField(User,  on_delete=models.CASCADE)
    slug = models.SlugField(max_length=50, default='')
    is_online = models.BooleanField(default=True)
    avatar = models.ImageField(blank=True, null=True)
    about = models.TextField(blank=True,)
    posts = models.IntegerField(default=0)
    friends = models.IntegerField(default=0)
    subscribers = models.IntegerField(default=0)
    subscriptions = models.IntegerField(default=0)

    access_messaging = models.IntegerField(**default_permission_settings)
    access_posts = models.IntegerField(**default_permission_settings)
    access_about = models.IntegerField(**default_permission_settings)
    access_albums = models.IntegerField(**default_permission_settings)
    access_images = models.IntegerField(**default_permission_settings)
    access_stats = models.IntegerField(**default_permission_settings)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = 'id{}'.format(self.user_id)
            UsersRelation.objects.create(
                main_user_profile=self, secondary_user_profile=self)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        if self.slug:
            return reverse('user_profile_url', kwargs={'slug': self.slug})
        return reverse('user_profile_url', kwargs={'slug': 'id' + self.pk})

    def get_chat_url(self):
        return reverse('private_chat_url', kwargs={'id': self.user.id})

    def get_relations_status(self, user: User):
        return UsersRelation.objects.get_or_create(
            main_user_profile=user.profile,
            secondary_user_profile=self
        )[0].get_relations_status()

    def is_messaging_accessible(self, user: User):
        relation_status = self.get_relations_status(user)
        return relation_status >= self.access_messaging


class UsersRelation(models.Model):
    main_user_profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='user1')
    secondary_user_profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='user2')
    is_friends = models.BooleanField(default=False)
    is_subscribed = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    related_object = models.OneToOneField(
        'self', on_delete=models.CASCADE, blank=True, null=True)

    def get_private_chat_url(self):
        return reverse(
            'private_chat_url', kwargs={'id': self.secondary_user_profile.id})

    def save(self, **kwargs):
        super().save(**kwargs)
        if self.secondary_user_profile != self.main_user_profile:
            if not self.related_object:
                relation_two = UsersRelation.objects.create(
                    main_user_profile=self.secondary_user_profile,
                    secondary_user_profile=self.main_user_profile,
                    related_object=self
                )
                self.related_object = relation_two
                self.save()

    def get_relations_status(self) -> int:
        if self.main_user_profile == self.secondary_user_profile:
            return 5  # its u
        elif self.related_object.is_blocked:
            return 1  # u block this user
        elif self.is_blocked:
            return -1  # u blocked by this person
        elif self.is_friends:
            return 4  # u r friends
        elif self.related_object.is_subscribed:
            return 3  # this is ur subscriber
        elif self.is_subscribed:
            return 2  # this is ur subscription
        else:
            return 0  # this person u don't know


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
