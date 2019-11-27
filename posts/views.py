from django.shortcuts import render
from .models import Post, Tag



def home_page(request):
    posts = Post.objects.all()
    return render(request, 'posts/first.html', context={'posts': posts})

def read_post(request, slug):
    post = Post.objects.get(slug__iexact=slug)
    return render(request, 'posts/read_post.html', context={'post': post })


def tags_list(request):
    tags = Tag.objects.all()
    return render(request, 'posts/tegs_list.html', context={'tags': tags})

def read_teg(request, slug):
    tag = Tag.objects.get(slug__iexact=slug)
    return render(request, 'posts/read_tag.html', context={'tag': tag })