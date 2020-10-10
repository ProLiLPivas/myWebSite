from django.shortcuts import redirect
from django.views import View


def redirect_posts(request):
    return redirect('posts_list_url', permanent=True)

