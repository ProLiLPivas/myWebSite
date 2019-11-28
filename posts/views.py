from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import  View

from .models import Post, Tag
from .utils import ReadObjectMixin
from .forms import TagForm


def home_page(request):
    posts = Post.objects.all()
    return render(request, 'posts/first.html', context={'posts': posts})


class ReadPost(ReadObjectMixin, View):
    model = Post
    template = 'posts/read_post.html'


def tags_list(request):
    tags = Tag.objects.all()
    return render(request, 'posts/tegs_list.html', context={'tags': tags})

class ReadTeg(ReadObjectMixin, View):
   model = Tag
   template = 'posts/read_tag.html'

class CreateTag(View):
    def get(self, request):
        form = TagForm()
        return render(request, 'posts/create_tag.html', context={'form': form })

    def post(self, request):
        bound_form = TagForm(request.POST)
        if bound_form.is_valid():
            new_tag = bound_form.save()
            return redirect(new_tag)
        return render(request, 'posts/create_tag.html', context={'form': bound_form})
