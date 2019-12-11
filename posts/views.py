from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import  View
from django.urls import reverse

from .models import Post, Tag
from .utils import ReadObjectMixin, CreateObjectMixin, UpdateObjectMixin, DeleteObjectMixin
from .forms import TagForm,PostForm


'''Post'''

def home_page(request):                     # first blog page
    posts = Post.objects.all()
    return render(request, 'posts/first.html', context={'posts': posts})


class ReadPost(ReadObjectMixin, View):      # read details about post
    model = Post
    template = 'posts/read_post.html'


class CreatePost(CreateObjectMixin, View):   # create new post
    model_form = PostForm
    template = 'posts/create_post.html'


class UpdatePost(UpdateObjectMixin, View):
    model = Post
    model_form = PostForm
    template = 'posts/update_post.html'

class DeletePost(DeleteObjectMixin, View):
    model = Post
    template = 'posts/delete_post.html'
    url = 'posts_list_url'



''' Tag '''

def tags_list(request):
    tags = Tag.objects.all()
    return render(request, 'posts/tegs_list.html', context={'tags': tags})


class ReadTeg(ReadObjectMixin, View):
   model = Tag
   template = 'posts/read_tag.html'


class CreateTag(CreateObjectMixin, View):   # create new tag
    model_form = TagForm
    template = 'posts/create_tag.html'


class UpdateTag(UpdateObjectMixin, View):
    model = Tag
    model_form = TagForm
    template = 'posts/update_tag.html'


class DeleteTag(DeleteObjectMixin, View):
    model = Tag
    template = 'posts/delete_tag.html'
    url = 'tags_list_url'