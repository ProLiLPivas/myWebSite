from django.shortcuts import render
from .models import Post



def home_page(request):
    posts = Post.objects.all()
    return render(request, 'posts/first.html', context={'posts': posts})


def read_post(request, slug):
    post = Post.objects.get(slug__iexact=slug)
    return render(request, 'posts/read_post.html', context={'post': post })