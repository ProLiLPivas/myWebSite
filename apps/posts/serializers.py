from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from rest_framework import serializers
from django.db.models import Q

# from apps.user_profile.models import Profile
from apps.posts.forms import *
from apps.posts.models import *


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

    user = UserSerializer()
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
            'slug',
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


def parseTags(tags_text):
            tag = ''
            tags = []
            for symbol in tags_text:
                if not symbol == ',':
                    tag += symbol
                else:
                    tags.append(tag)
                    tag = ''
            tags.append(tag)
            return tags







class FeedMixin:
    template = None
    query_parameters = Q()
    ordering = ('-date_publication',)

    def get(self, request, slug=''):  # feed # only friends # popular   # all
        if request.is_ajax():
            if slug and not self.query_parameters[1]:
                query = Q((self.query_parameters[0], slug))
            else:
                query = Q(self.query_parameters)
            posts = Post.objects.filter(query).order_by(*self.ordering)
            feed_dict = {}
            users_dict = {'id': request.user.id, 'username': request.user.username,  'is_staff': request.user.is_staff}
            print(JsonResponse({'posts': feed_dict, 'user': users_dict, 'url': request.path}, status=200))
            return JsonResponse({'posts': feed_dict, 'user': users_dict, 'url': request.path}, status=200)
        return render(request, self.template, context={'url': request.path, 'slug': slug})









class LikeMixin:
    model = None

    def post(self, request):
        like, model_obj = PostUtils.chose_instance(request.POST['object_id'], request.user, self.model)
        response = PostUtils.like_object(like, model_obj)
        if response:
            return JsonResponse(response, status=200)
        else:
            return HttpResponse(status=403)





class PostUtils:
    ''' '''
    @staticmethod
    def create_post(data, user):
        bound_form = PostForm(data)
        if bound_form.is_valid():
            new_post = bound_form.save(commit=False)
            new_post.user = user
            profile = user.profile
            profile.posts += 1
            profile.save()
            new_post.save()
            return new_post

    @staticmethod
    # def create_or_get_tags(t, new_obj):
    #     tags = PostSerializer.parseTags(t)
    #     tags_dict = []
    #     if tags != ['']:
    #         for tag in tags:
    #             new_tag = Tag.objects.get_or_create(title=tag.__str__())
    #             new_obj.tag.add(new_tag[0])
    #             tags_dict.append(model_to_dict(new_tag[0]))
    #     return tags_dict

    @staticmethod
    def update_post(data, post_id, user):
        post = Post.objects.get(id=post_id)
        if post.user == user:
            bound_form = PostForm(data, instance=post)

            if bound_form.is_valid():
                new_obj = bound_form.save()
                new_obj.is_changed = True
                new_obj.save()
                return new_obj, 200
        return None, 403

    @staticmethod
    def del_post(id , user):
        """
        :param id:
        :param user:
        :return:
        """
        obj = Post.objects.get(id=int(id))
        if user == obj.user or user.is_staff:
                user_object = Profile.objects.get(id=user.id)
                user_object.posts -= 1
                user_object.save()
                obj.delete()
                return {'posts_amount': user_object.posts}
        else:
            return None

    @staticmethod
    def create_comment(bound_form, user, id):
        """
        :param bound_form:
        :param user:
        :param id:
        :return:
        """
        post = Post.objects.get(id=id)
        if  post.comment_permission <= PostUtils.get_permission(post, user):
            if bound_form.is_valid():
                new_comment = bound_form.save(commit=False)
                if new_comment.text != 'null':
                    post.comments_amount += 1
                    new_comment.post = post
                    new_comment.user = user
                    new_comment.save()
                    post.save()
                    # return PostSerializer.new_comment_to_dict(new_comment, post.comments_amount,  user), 200
            return None, 403
        return None, 403


    @staticmethod
    def update_comment(comment_id, text, user):
        com_obj = Comment.objects.get(id=comment_id)
        if com_obj.user == user:
            bound_form = CommentForm({'text': text}, instance=com_obj)
            if bound_form.is_valid():
                comment = bound_form.save(commit=False)
                comment.is_changed = True
                comment.save()
                return text, 200

    @staticmethod
    def del_comment(id, post_id, user):
        obj = Comment.objects.get(id=int(id))
        post_object = Post.objects.get(id=int(post_id))
        if user == obj.user or user == post_object.user or user.is_staff:
            post_object.comments_amount -= 1
            post_object.save()
            obj.delete()
            return {'comment_amount': post_object.comments_amount}
        else: return None

    @staticmethod
    def like_object(like, model_obj):
        if like != 0 and model_obj != 0:
            if not like.exist:
                like.exist = True
                model_obj.likes_amount += 1
            else:
                like.exist = False
                model_obj.likes_amount -= 1
            like.save()
            model_obj.save()
            return {'is_liked': like.exist, 'amount': model_obj.likes_amount}
        else: return []

    @staticmethod
    def chose_instance(id, user, model):
        model_obj = model.objects.get(id=int(id))
        if model == Post:
            if model_obj.like_permission <= PostUtils.get_permission(model_obj, user):
                return (Like.objects.get_or_create(user=user, post=model_obj))[0], model_obj
            else: return 0, 0
        elif model == Comment:
            return (Like.objects.get_or_create(user=user, comment=model_obj))[0], model_obj
        else:
            return None, None

    @staticmethod
    def repost(post, user):
        if post.repost_permission <= PostUtils.get_permission(post, user):
            pass


    @staticmethod
    def get_permission(post, user):
        return UsersRelation.get_or_create_relations(
            post.user.profile, user.profile).get_relations_status()


    @staticmethod
    def set_post_permissions(data, user):
        post = Post.objects.get(id=int(data['post_id']))
        if post.user == user:
            bound_form = PostSettingsForm(data, instance=post)
            if bound_form.is_valid() and post.user == user:
                bound_form.save()
                return 200
        return 403



