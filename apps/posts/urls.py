from django.urls import path
from .views import *


urlpatterns = [
    path('', home_page, name='posts_list_url'),

    path('post/<str:slug>/', ReadPost.as_view(), name='read_post_url'),
    path('post/create/', CreatePost.as_view(), name='create_post_url'),
    path('post/update/', UpdatePost.as_view(), name='update_post_url'),
    path('post/delete/', DeletePost.as_view(), name='delete_post_url'),
    path('like/', LikePost.as_view(), name='like_post_url'),

    path('comment/post=<int:id>/', Comments.as_view(), name='comment_url'), # split on comment create and comment read
    # path('comment/update/', ),
    path('comment/delete/', DeleteComment.as_view(), name='delete_comment_url'),
    path('comment/like', LikeComment.as_view(), name='like_comment_url'),


    # path('repost=<int:id>/chat'),
    # path('repost=<int:id>/wall'),



    path('tags/', tags_list, name='tags_list_url'),
    # path('tags/create/', CreateTag.as_view(), name='create_tag_url'),
    path('tags/<str:slug>/', ReadTeg.as_view() , name='read_tag_url'),
    # path('tags/<str:slug>/update/', UpdateTag.as_view(), name='update_tag_url'),
    # path('tags/<str:slug>/delete/', DeleteTag.as_view(), name='delete_tag_url'),
]
