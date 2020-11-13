from django.shortcuts import redirect
from django.views import View


def redirect_posts(request):
    return redirect('feed_url', permanent=True)

