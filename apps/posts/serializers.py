from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from rest_framework import serializers
from django.db.models import Q

# from apps.user_profile.models import Profile
from apps.posts.forms import *
from apps.posts.models import *
from apps.user_profile.models import Profile


class UserSerializer(serializers.ModelSerializer):

    avatar = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'url', 'avatar', )

    def get_url(self, obj):
        return obj.profile.get_absolute_url()

    def get_avatar(self, obj):
        if obj.profile.avatar:
            return obj.profile.avatar
        return None



class TagSerializer(serializers.ModelSerializer):

    url = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        exclude = ('slug',)

    def get_url(self, obj):
        return obj.get_absolute_url()


class TagsListSerializer(TagSerializer):

    length = serializers.SerializerMethodField()

    def get_length(self, obj: Tag):
        return len(obj)

class PostSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = (
            'see_comments_permission',
            'comment_permission',
            'like_permission',
            'repost_permission',
            'see_statistic_permission',
            'see_author_permission',
            'see_post_permission',
        )


class CommentsSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'

    def get_is_liked(self, obj: Post):
        return CommentLike.get_is_liked(obj, self.context['request'].user)


class FeedSerializer(serializers.ModelSerializer):

    requested_from: User = None
    relation_statuses_dict: dict = None

    user = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    post_statistic = serializers.SerializerMethodField()
    permission_settings = serializers.SerializerMethodField()
    tag = TagSerializer(many=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.requested_from: User = self.context['request'].user
        self.relation_statuses_dict = self.get_relation_statuses_dict()

    class Meta:
        model = Post
        exclude = (
            'likes_amount',
            'comments_amount',
            'reposts_amount',
            'see_comments_permission',
            'comment_permission',
            'like_permission',
            'repost_permission',
            'see_statistic_permission',
            'see_author_permission',
            'see_post_permission'
        )

    def to_representation(self, instance: Post):
        if not self.relation_statuses_dict.get(instance.user):
            return
        if not instance.is_post_accessible(self.requested_from):
            return
        return super().to_representation(instance)

    def get_user(self, obj: Post):
        if obj.see_author_permission < self.relation_statuses_dict.get(obj.user):
            return UserSerializer(obj.user).data
        return {'id': 0, 'username': 'Anonimus', 'url': '', 'avatar': None,}

    def get_url(self, obj: Post):
        return obj.get_absolute_url()

    def get_is_liked(self, obj: Post):
        return PostLike.get_is_liked(obj, self.requested_from)

    def get_post_statistic(self, obj: Post):
        permissions = obj.get_statistic_permissions_dict(
            self.relation_statuses_dict.get(obj.user))
        stats_dict = {
            'likes_amount': None,
            'comments_amount': None,
            'reposts_amount': None,
        }
        if permissions['see_statistic_permission']:
            if permissions['like_permission']:
                stats_dict['likes_amount'] = obj.likes_amount
            if permissions['comment_permission']:
                stats_dict['comments_amount'] = obj.comments_amount
            if permissions['repost_permission']:
                stats_dict['reposts_amount'] = obj.reposts_amount
        return stats_dict

    def get_permission_settings(self, obj):
        return PostSettingsSerializer(obj).data

    def get_relation_statuses_dict(self):
        users = list(set([post.user for post in self.instance]))
        relation_statuses_dict = {}
        for user in users:
            relation_status = UsersRelation.objects.get(
                main_user_profile=self.requested_from.profile,
                secondary_user_profile=user.profile
            ).get_relations_status()
            if relation_status < user.profile.access_posts:
                continue
            relation_statuses_dict.update({user: relation_status})
        return relation_statuses_dict


class SinglePostSerializer(FeedSerializer):

    comments = serializers.SerializerMethodField()

    def get_comments(self, obj: Post):
       return CommentsSerializer(
            Comment.objects.filter(post=obj),
            many=True,
            context=self.context
        ).data


class CreatePostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('title', 'body',)

    def create(self, validated_data):
        validated_data.update(self.context.get('user'))
        validated_data.update(self.context.get('permission_settings'))
        post = Post.objects.create(**validated_data)
        for tag in self.context.get('tags'):
            post.tag.add(Tag.objects.get_or_create(title=tag)[0])
        return post


class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            'title',
            'body',
            'see_comments_permission',
            'comment_permission',
            'like_permission',
            'repost_permission',
            'see_statistic_permission',
            'see_author_permission',
            'see_post_permission',
        )

    def update(self, instance, validated_data):
        validated_data.update(self.context.get('permission_settings'))
        UpdateSerializer.update_tags(instance, self.context.get('tags'))
        i = super().update(instance, validated_data)
        return i

    @staticmethod
    def update_tags(instance, tags):
        query = Q()
        for tag in tags:
            query = query | Q(title=tag)
        instance.tag.remove(*list(instance.tag.exclude(query)))
        existing_tags = list(instance.tag.all().values('title'))
        for tag in tags:
            if not {'title': tag} in existing_tags:
                instance.tag.get_or_create(title=tag)


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('text',)

    def create(self, validated_data):
        validated_data.update(self.context)
        comment = Comment.objects.create(**validated_data)
        return comment


a = {"text": "1111"}

b = {
    "permission_settings": {
        "see_comments_permission": 3,
        "comment_permission": 2,
        "like_permission": 1,
        "repost_permission": 0,
        "see_statistic_permission": 0,
        "see_author_permission": 0,
        "see_post_permission": 1
    },
    "tags": "0,1336",
    "title": "111",
    "body": "_ . _ . _"
}