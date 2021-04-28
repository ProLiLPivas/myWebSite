from django.contrib.auth.models import User
from django.db.models import Q
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from rest_framework import serializers

from apps.posts.models import Post
from apps.posts.serializers import FeedSerializer
from apps.user_profile.models import Profile, UsersRelation



class ProfileSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            'access_messaging',
            'access_posts',
            'access_about',
            'access_albums',
            'access_images',
            'access_stats',
        )


class ProfileSerializer(serializers.ModelSerializer):

    relations_status = None

    user = serializers.StringRelatedField()
    access_settings = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()
    albums = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()
    about = serializers.SerializerMethodField()
    msg_url = serializers.SerializerMethodField()
    # extra_kwargs = {'relations_status': relations_status}

    class Meta:
        model = Profile
        fields = ('id', 'user', 'albums', 'avatar', 'stats', 'about', 'is_online',
            'access_settings', 'msg_url', 'posts', )


    def to_representation(self, instance: Profile):
        self.relations_status = \
            instance.get_relations_status(self.context['user'])
        return super().to_representation(instance)

    def get_posts(self, obj: Profile):
        if self.relations_status < obj.access_posts:
            return
        queryset = Post.objects.filter(user=obj.user)
        return FeedSerializer(queryset, many=True, context=self.context).data

    def get_avatar(self, obj: Profile):
        if self.relations_status < obj.access_images:
            return
        if obj.avatar:
            return obj.avatar
        return # will return image after image update

    def get_albums(self, obj: Profile):
        if self.relations_status < obj.access_images:
            return
        return # will return albums after image update

    def get_stats(self, obj: Profile):
        if self.relations_status < obj.access_stats:
            return
        return {
            'posts_amount': obj.posts,
            'friends_amount': obj.friends,
            'subscribers_amount': obj.subscribers,
            'subscriptions_amount': obj.subscriptions,
        }

    def get_about(self, obj: Profile):
        if self.relations_status < obj.access_about:
            return
        return obj.about

    def get_access_settings(self, obj):
        return ProfileSettingsSerializer(obj).data

    def get_msg_url(self, obj: Profile):
        if obj.is_messaging_accessible(self.context['user']):
            return obj.get_chat_url()

    def rel_status(self, obj: Profile):
        return obj.get_relations_status(self.context['user'])

class RelatedUsersSerializer(ProfileSerializer):
    url = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = ('id', 'user', 'avatar', 'is_online', 'url', 'msg_url')

    def get_url(self, obj: Profile):
        return obj.get_absolute_url()

    def to_representation(self, instance: Profile):
        representation = super().to_representation(instance)
        if self.relations_status < instance.access_stats:
            return
        return representation


class EditProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ('avatar', 'about', 'slug')
