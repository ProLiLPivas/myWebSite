from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import model_to_dict
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse, HttpResponse

from apps.posts.utils import PostUtils, PostSerializer
from apps.user_profile.models import Profile
from .forms import *
from .models import *


class FeedMixin(View):
    template = None
    filter = Q()
    global slug

    def get(self, request, slug=None):  # feed # only friends # popular   # all
        if request.is_ajax():
            posts = Post.objects.filter()
            feed_dict = PostSerializer.feed_to_dict(posts, request.user)
            users_dict = {'id': request.user.id, 'is_staff': request.user.is_staff}
            return JsonResponse({'posts': feed_dict, 'user': users_dict, }, status=200)
        return render(request, self.template)


class Feed(FeedMixin, View):
    template = 'posts/feed.html'
    posts = Post.objects.all()


class FeedForProfile:
    pass
    # posts = Post.objects.filter(user__id=user_id)


class ReadTeg(FeedMixin, View):
    slug = None
    posts = Post.objects.filter(tag__title=slug).order_by('-likes_amount', '-comments_amount')
    template = 'posts/read_tag.html'


class ReadPost(View):  # read details about post

    template = 'posts/read_post.html'

    def get(self, request, slug):  # feed # only friends # popular   # all
        pass
        # if request.is_ajax():
        #     posts = Post.objects.filter(id=slug)
        #     print(posts)
        #     feed_dict = PostSerializer.feed_to_dict(posts, request.user)
        #     users_dict = {'id': request.user.id, 'is_staff': request.user.is_staff}
        #     return JsonResponse({'posts': feed_dict, 'user': users_dict, }, status=200)
        #
        # return render(request, self.template)

    # posts = Post.objects.filter(user=request.user)  # for my profile
    # q = Q(user__id=2) | Q(user__id=5)
    # posts = Post.objects.filter(q) # for any filter


def tags_list(request):
    tags = Tag.objects.all()
    return render(request, 'posts/tegs_list.html', context={'tags': tags})


class LikeMixin:
    model = None

    def post(self, request):
        response = PostUtils.like_object(*PostUtils.chose_instance(request.POST['object_id'], request.user, self.model))
        if response:
            return JsonResponse(response, status=200)
        else:
            return HttpResponse(status=403)


class LikePost(LikeMixin, LoginRequiredMixin, View):
    model = Post


class LikeComment(LikeMixin, LoginRequiredMixin, View):
    model = Comment


class Comments(View):
    def get(self, request, id):
        comments = PostSerializer.comments_to_dict(id, request.user)
        return JsonResponse({'comments': comments}, status=200)

    def post(self, request, id):
        bound_form = CommentForm(request.POST)
        new_comment, status = PostUtils.create_comment(bound_form, request.user, id)
        if new_comment:
            return JsonResponse({'comment': new_comment}, status=status)
        else:
            return HttpResponse(status=status)


class UpdateComment(View):
    def post(self, request):
        new_text, status = PostUtils.update_comment(request.POST['comment_id'], request.POST['new_text'], request.user)
        return JsonResponse({'text': new_text}, status=status)


class DeleteComment(LoginRequiredMixin, View):
    def post(self, request):
        amount = PostUtils.del_comment(request.POST['id'], request.POST['post_id'], request.user)
        if amount:
            return JsonResponse(amount, status=200)
        return HttpResponse(status=403)


class CreatePost(View):
    model = Post
    model_form = PostForm

    def post(self, request):
        new_post = PostUtils.create_post(request.POST, request.user)
        tags = PostUtils.create_or_get_tags(request.POST['tags'], new_post)
        post_dict = model_to_dict(new_post)
        post_dict['tag'] = tags

        return JsonResponse({'post': post_dict}, status=200)


class UpdatePost(View):
    model = Post
    model_form = PostForm

    def post(self, request):
        updated_post, status = PostUtils.update_post(request.POST, request.POST['post_id'], request.user)
        tags = PostUtils.create_or_get_tags(request.POST['tags'], updated_post)
        return JsonResponse({'tag': tags}, status=status)


class DeletePost(LoginRequiredMixin, View):
    def post(self, request):
        amount = PostUtils.del_post(request.POST['id'], request.user)
        if amount:
            return JsonResponse(amount, status=200)
        return HttpResponse(status=403)


class PostSettings(View):
    def post(self, request):
        http_status = PostUtils.set_post_permissions(request.POST, request.user)
        return HttpResponse(status=http_status)


# class Repost(View):
#     pass

# class DeleteTag(LoginRequiredMixin, DeleteObjectMixin, View):
#     model = Tag
#     template = 'posts/delete_tag.html'
#     url = 'tags_list_url'
#     raise_exception = True


# class Repost:
#     def get(self, request):
#         try:
#             chats = Connection2Chat.objects.filter(user=request.user)
#             return JsonResponse({'chats': chats}, status=200)
#         except Connection2Chat.DoesNotExist:
#             friends = Relations.objects.filter(user_one__user=request.user, is_friends=1)
#             return JsonResponse({'chats': []}, status=200)
#
#     def post(self, request):
#         is_2chat = False
#         response = None
#         if is_2chat:
#             pass
#         else:
#             pass
#
#     def formRepost2Wall(self):
#         pass
#     def formRepost2Chat(self):
#         pass
