from django.shortcuts import redirect


def redirect_posts(request):
    return redirect('posts_list_url',permanent=True)