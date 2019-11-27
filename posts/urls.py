from django.urls import path

from .views import *

urlpatterns = [
    path('', home_page, name='posts_list_url'),
    path('post/<str:slug>', ReadPost.as_view() , name='read_post_url' ),
    path('tags/', tags_list, name='tags_list_url'),
    path('tags/<str:slug>', ReadTeg.as_view() , name='read_tag_url')
]