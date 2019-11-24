from django.urls import path

from .views import *

urlpatterns = [
    path('', home_page, name='posts_list_url'),
    path('post/<str:slug>', read_post, name='read_post_url' )
]