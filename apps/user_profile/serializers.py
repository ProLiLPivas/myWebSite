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

    class Meta:
        model = Profile
        fields = ('id', 'user', 'albums', 'avatar', 'stats', 'about', 'is_online',
            'access_settings', 'msg_url', 'posts',)

    def to_representation(self, instance: Profile):
        self.relations_status = \
            instance.get_relations_status(self.context['request'].user)
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
        return obj.get_chat_url()


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






def get_profile_and_relations(slug, your_profile):
    profile = Profile.objects.get(slug__iexact=slug)
    relation = UsersRelation.objects.get_or_create(
        main_user_profile=your_profile, secondary_user_profile=profile)[0]
    return profile, relation


def get_profile_context(slug, users_profile, path):
    profile, relation_with_you = get_profile_and_relations(slug, users_profile)
    status = relation_with_you.get_relations_status()

    if status == -1:
        return {'profile': {'user': profile.user, }, 'status': status}

    profile_dict = model_to_dict(profile)
    profile_dict['username'] = profile.user.username
    return {
        'profile': profile_dict,
        'relations': relation_to_dict(relation_with_you),
        'status': status,
        'slug': slug,
        'url': path,
    }


def get_relations_list(query):
    users_relation_queryset = list(UsersRelation.objects.filter(Q(*query)))
    return [model_to_dict(user.secondary_user_profile) for user in
            users_relation_queryset]


def relation_to_dict(relation):
    if relation:
        print(relation.is_friends , relation.is_subscribed ,
              relation.is_blocked)
        return {
            'is_friends': int(relation.is_friends) ,
            'is_subscribed': int(relation.is_subscribed) ,
            'is_block': int(relation.is_blocked)
        }
    return []


def subscribe_or_unsubscribe(_, relation_obj):
    # _ must be here without it dont work
    sub_changes = (+1 , -1)[relation_obj.is_subscribed]

    relation_obj.is_subscribed = not relation_obj.is_subscribed
    relation_obj.main_user_profile.subscriptions += sub_changes
    relation_obj.secondary_user_profile.subscribers += sub_changes

    relation_obj.main_user_profile.save()
    relation_obj.secondary_user_profile.save()
    relation_obj.save()


def add_or_remove_friends(_, relation_obj):
    # _ must be here without it dont work
    subscribe_or_unsubscribe(_ , relation_obj)
    sub_changes = (+1 , -1)[relation_obj.is_friends]

    relation_obj.is_friends = not relation_obj.is_friends
    relation_obj.related_object.is_friends = not relation_obj.related_object.is_friends
    relation_obj.main_user_profile.friends += sub_changes
    relation_obj.secondary_user_profile.friends += sub_changes

    relation_obj.main_user_profile.save()
    relation_obj.secondary_user_profile.save()
    relation_obj.save()
    relation_obj.related_object.save()


def block_unblock_user(_, relation_obj):
    # _ must be here without it dont work
    relation_obj.related_object.is_blocked = not relation_obj.is_blocked
    relation_obj.save()


def change_relations_status(func_obj, slug, users_profile):
    relation_with_you = UsersRelation.objects.get(
        main_user_profile=users_profile, secondary_user_profile__slug=slug)
    func_obj(relation_with_you)

class RelatedUsersView:
    """ """
    key = ''
    slug_query_parameter: str = ''
    second_condition: tuple = ('id', 1)
    post_action_func = lambda *args: print('u dont using any func')
    is_have_post_method: bool = True
    template = 'profile/friends.html'

    def get(self, request, slug=None):
        if slug and not request.is_ajax():
            return HttpResponse(status=404)
        elif not slug:
            if not request.is_ajax():
                return render(request, self.template)
            else:
                slug = request.user.profile.slug
        query = ((self.slug_query_parameter, slug), self.second_condition)
        rel = get_relations_list(query)

        for user in rel:  # !!! remove later !!!
            user['avatar'] = ''
            user['url'] = '/user/' + user['slug'] + '/'
            user['chat_url'] = '/messages/id=' + str(user['id']) + '/'
        return JsonResponse({'related_users': rel, 'key': self.key}, status=200)

    def post(self, request, slug):
        if self.is_have_post_method:
            change_relations_status(self.post_action_func, slug, request.user.profile)
            return redirect('/user/' + slug)
        return HttpResponse(status=405)
