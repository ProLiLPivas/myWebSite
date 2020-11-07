from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse, HttpResponse

from apps.message.models import Connection2Chat
from apps.relations.models import Relations
from apps.user_profile.models import Profile
from .forms import *
from .models import *


def home_page(request):                     # first blog page
    posts = Post.objects.all()
    return render(request, 'posts/feed.html')# , context={'posts': posts, 'user': request.user})

class GetFeed(View):
    def get(self, request):
        posts = Post.objects.all()
        dict = [model_to_dict(post) for post in posts]

        for post in dict:
            if post['tag']:
                tags = []
                for tag in post['tag']:
                    m2d = model_to_dict(tag)
                    tags.append(m2d)
                post['tag'] = tags

        return JsonResponse({
            'posts': dict,
            'user': {'id': request.user.id, 'is_staff': request.user.is_staff}
        }, status=200)

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


class Create_or_Update_Objects:                 # create new post         LoginRequiredMixin, CreateObjectMixin,
    model_form = None

    def post(self, request):
        if (request.POST['is_update']) == 'true':
            print(request.POST)
            bound_form = self.model_form(request.POST, instance=Post.objects.get(id=request.POST['post_id']))
            if bound_form.is_valid():
                new_obj = bound_form.save()
                tags = self.parseTags(request.POST['tags'])

                if tags != ['']:
                    t = []
                    for tag in tags:
                        new_tag = Tag.objects.get_or_create(title=tag.title, slug=tag.title)
                        new_obj.tag.add(new_tag[0])
                        t.append(model_to_dict(new_tag[0]))
                data = {'tag': t}
                new_obj.save()
                return JsonResponse(data, status=200)
        else:
            print(request.POST)
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

                t = []
                for tag in tags:
                    new_tag = Tag.objects.get_or_create(title=tag.title, slug=tag.title)
                    new_obj.tag.add(new_tag[0])
                    t.append(model_to_dict(new_tag[0]))
                m2d = model_to_dict(new_obj)
                m2d['tag'] = t
                data = {'post': m2d}
                new_obj.save()
                return JsonResponse(data, status=200)
        return JsonResponse({}, status=200)


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

class UpdatePost(Create_or_Update_Objects, View):
    model = Post
    model_form = PostForm


class UpdateComment(View):
    def post(self, request):
        com_obj = Comment.objects.get(id=request.POST['comment_id'])
        new_text = request.POST['new_text']
        bound_form = CommentForm({'text': new_text}, instance=com_obj)
        if bound_form.is_valid():
            bound_form.save()
            return JsonResponse({'text': new_text})


class DeleteObjectMixin:
    '''

    '''
    model = None

    def post(self, request):
        obj = self.model.objects.get(id=request.POST['id'])
        if self.model == Post:
            if request.user == obj.user or request.user.is_staff:    # checking that user deleting this post is creator or admin
                user_object = Profile.objects.get(id=request.user.id)
                user_object.posts -= 1
                user_object.save()
                obj.delete()
                return JsonResponse({'posts_amount': user_object.posts})
            else: return HttpResponse(status=403)
        elif self.model == Comment:
            post_object = Post.objects.get(id=request.POST['post_id'])
            if request.user == obj.user or request.user == post_object.user or request.user.is_staff:
                post_object.comments_amount -= 1
                post_object.save()
                obj.delete()
                return JsonResponse({'comment_amount': post_object.comments_amount})
            else: return HttpResponse(status=403)


class DeletePost(DeleteObjectMixin, LoginRequiredMixin, View):
    model = Post

class DeleteComment(DeleteObjectMixin, LoginRequiredMixin, View):
    model = Comment

# class DeleteTag(LoginRequiredMixin, DeleteObjectMixin, View):
#     model = Tag
#     template = 'posts/delete_tag.html'
#     url = 'tags_list_url'
#     raise_exception = True





