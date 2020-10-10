from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse

from apps.message.models import Connection2Chat
from apps.relations.models import Relations
from apps.user_profile.models import Profile
from .forms import *
from .models import *


def home_page(request):                     # first blog page
    posts = Post.objects.all()
    return render(request, 'posts/feed.html', context={'posts': posts, 'user': request.user})

def tags_list(request):
    tags = Tag.objects.all()
    return render(request, 'posts/tegs_list.html', context={'tags': tags})


class ReadObjectMixin:
    model = None
    template = None

    def get(self, request, slug):
        obj = get_object_or_404(self.model , slug__iexact=slug)
        return render(request, self.template, context={
            self.model.__name__.lower(): obj, 'admin_obj': obj, 'read_obj': True
        })

class ReadPost(ReadObjectMixin, View):      # read details about post
    model = Post
    template = 'posts/read_post.html'

class ReadTeg(ReadObjectMixin, View):
   model = Tag
   template = 'posts/read_tag.html'


class LikeMixin:
    model = None
    def post(self, request):
        obj = self.model.objects.get(id=request.POST['object_id'])
        like = self.chose_instance(request.user, obj)

        if not like.exist:
            like.exist = True
            obj.likes_amount += 1
            like.save()
            obj.save()
            return JsonResponse({'is_liked': True, 'amount': obj.likes_amount}, status=200)
        else:
            like.exist = False
            obj.likes_amount -= 1
            like.save()
            obj.save()
            return JsonResponse({'is_liked': False, 'amount': obj.likes_amount}, status=200)

    def chose_instance(self, user, obj):
        if self.model == Post:
            return (Like.objects.get_or_create(user=user, post=obj))[0]
        elif self.model == Comment:
            return (Like.objects.get_or_create(user=user, comment=obj))[0]
        else:
            return

class LikePost(LikeMixin, View):
    model = Post

class LikeComment(LikeMixin, View):
    model = Comment



class Comments(View):
    def get(self, request, id):
        comments = list(Comment.objects.filter(post__id=id).values())
        if comments:
            return JsonResponse({'comments': comments}, status=200)
        else:
            return JsonResponse({'comments': None }, status=200)

    def post(self, request, id):
        bound_form = CommentForm(request.POST)

        if bound_form.is_valid():
            new_comment = bound_form.save(commit=False)
            if new_comment.text != 'null':
            # new_comment.user = request.user.id
                post_obj = Post.objects.get(id=id)
                post_obj.comments_amount += 1
                new_comment.post = post_obj
                new_comment.user = request.user
                new_comment.save()
                post_obj.save()

                return JsonResponse({
                    'comments': model_to_dict(new_comment),
                    'comment_amount': post_obj.comments_amount,
                },status=200)
            else:
                return JsonResponse({'comments': ''}, status=200)

class Repost:
    def get(self, request):
        try:
            chats = Connection2Chat.objects.filter(user=request.user)
            return JsonResponse({'chats': chats}, status=200)
        except Connection2Chat.DoesNotExist:
            friends = Relations.objects.filter(user_one__user=request.user, is_friends=1)
            return JsonResponse({'chats': []}, status=200)

    def post(self, request):
        is_2chat = False
        response = None
        if is_2chat:
            pass
        else:
            pass

    def formRepost2Wall(self):
        pass
    def formRepost2Chat(self):
        pass


class Create_or_Update_Objects:   # create new post         LoginRequiredMixin, CreateObjectMixin,
    model_form = None
    raise_exception = True

    def post(self, request):
        print(request.POST['is_update'])
        if (request.POST['is_update']) == True:
            bound_form = self.model_form(request.POST, instance=Post.objects.get(id=request.POST['post_id']))
            if bound_form.is_valid():
                bound_form.save()
                tags = self.parseTags(request.POST['tags'])
                for tag in tags:
                    new_tag = Tag.objects.get_or_create(title=tag.title, slug=tag.title)
                    bound_form.tag.add(new_tag[0])
                bound_form.save()
        else:
            bound_form = self.model_form(request.POST)
            if bound_form.is_valid():
                new_obj = bound_form.save(commit=False)
                if self.model_form == PostForm:
                    new_obj.user_id = request.user.id
                    user_object = Profile.objects.get(id=request.user.id)
                    user_object.posts += 1
                    user_object.save()
                new_obj.save()

                tags = self.parseTags(request.POST['tags'])
                for tag in tags:
                    new_tag = Tag.objects.get_or_create(title=tag.title, slug=tag.title)
                    new_obj.tag.add(new_tag[0])
                new_obj.save()
        return JsonResponse({'form': ''}, status=200)

    def parseTags(self, tags_text):
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


class CreatePost(Create_or_Update_Objects, View):
    model = Post
    model_form = PostForm
    raise_exception = True

class UpdatePost(Create_or_Update_Objects, View):
    model = Post
    model_form = PostForm

# class UpdateObjectMixin:
#     model = None
#     model_form = None
#     template = None
#
#     def get(self, request, slug):
#         obj = self.model.objects.get(slug__iexact=slug)
#         bound_form = self.model_form(instance=obj)
#         return render(request, self.template , context={'form': bound_form, self.model.__name__.lower() : obj})
#
#     def post(self, request, slug):
#         obj = self.model.objects.get(slug__iexact=slug)
#         bound_form = self.model_form(request.POST, instance=obj)
#
#         if bound_form.is_valid():
#             new_obj = bound_form.save()
#             return redirect(new_obj)
#         return render(request, self.template,
#         context={'form': bound_form, self.model.__name__.lower() : obj})
#
# class UpdatePost(LoginRequiredMixin, UpdateObjectMixin, View):
#     model = Post
#     model_form = PostForm
#     template = 'posts/update_post.html'
#
# class UpdateTag(LoginRequiredMixin, UpdateObjectMixin, View):
#     model = Tag
#     model_form = TagForm
#     template = 'posts/update_tag.html'
#     raise_exception = True
#
# class UpdateComment:
#     pass


class DeleteObjectMixin:
    model = None

    def post(self, request):

        obj = self.model.objects.get(id=request.POST['id'])
        if self.model == Post:
            # if user == post_user_id.....     # checking that user deleting this post is creator or admin
            user_object = Profile.objects.get(id=request.user.id)
            user_object.posts -= 1
            user_object.save()
        if self.model == Comment:
            post_object = Post.objects.get(id=request.POST['post_id'])
            post_object.comments_amount -= 1
            post_object.save()
            obj.delete()
            return JsonResponse({'comment_amount': post_object.comments_amount})
        obj.delete()



class DeletePost(DeleteObjectMixin, View): #LoginRequiredMixin,
    model = Post

class DeleteComment(DeleteObjectMixin, View):
    model = Comment

# class DeleteTag(LoginRequiredMixin, DeleteObjectMixin, View):
#     model = Tag
#     template = 'posts/delete_tag.html'
#     url = 'tags_list_url'
#     raise_exception = True





