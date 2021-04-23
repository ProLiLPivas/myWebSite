from django.urls import path
from .views import *


urlpatterns = [
    path('', Feed.as_view(), name='feed_url'), #
    path('top/', MostPopularFeed.as_view(), name='top_feed_url'),
    # path('friends/', FriendsFeed.as_view(), name='friends_feed_url'), #
    # path('subscribers/', SubscribersFeed.as_view(), name='subscribers_feed_url'), #
    # path('subscription/', SubscriptionFeed.as_view(), name='subscription_feed_url'), #
    path('user=<str:slug>/', FeedForProfile.as_view(), name='user_feed_url'), #

    path('post/create/', CreatePost.as_view(), name='create_post_url'),
    path('post/update/', UpdatePost.as_view(), name='update_post_url'),
    path('post/delete/', DeletePost.as_view(), name='delete_post_url'),
    path('post/permissions/', PostSettings.as_view(), name='settings_post_url'),
    path('post=<int:slug>/', ReadPost.as_view(), name='read_post_url'), #
    path('like/', LikePost.as_view(), name='like_post_url'),

    path('comment/post=<int:id>/', Comments.as_view(), name='comment_url'),
    path('comment/update/', UpdateComment.as_view(), name='update_comment_url'),
    path('comment/delete/', DeleteComment.as_view(), name='delete_comment_url'),
    path('comment/like/', LikeComment.as_view(), name='like_comment_url'),
    # path('repost=<int:id>/chat'),
    # path('repost=<int:id>/wall'),
    path('tags/', Tags.as_view(), name='tags_list_url'),
    path('tag=<str:slug>/', ReadTag.as_view() , name='read_tag_url'),
    # path('tags/<str:slug>/update/', UpdateTag.as_view(), name='update_tag_url'),
    # path('tags/<str:slug>/delete/', DeleteTag.as_view(), name='delete_tag_url'),

    path('api/', APIFeed.as_view()),
    path('post=<int:id>/api/', APIPost.as_view()),
    path('comment/post=<int:id>/api/', APIComments.as_view()),
    path('tags/api/', APITags.as_view(), name='tags_list_url'),
    path('tag=<str:slug>/api/', APITag.as_view(), ),
]

