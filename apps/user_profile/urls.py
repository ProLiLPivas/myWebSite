from django.urls import path
from .views import *


urlpatterns = [

    # path('all/', All.as_view(), name='all_users_list_url'),
    path('me/', MyProfile.as_view(), name='get_my_profile'),
    path('me/settings/', ProfileSettings.as_view(), name='profile_settings'),
    path('subscribers/', Subscribers.as_view(), name='subscribers_url'),
    path('subscriptions/', Subscriptions.as_view(), name='subscriptions_url'),
    path('friends/', Friends.as_view(), name='friends_url'),
    path('blacklist/', BlackList.as_view(), name='blacklist_url'),


    path('<str:slug>/', UserProfile.as_view(), name='user_profile_url'),
    path('<str:slug>/subscribers/', Subscribers.as_view()),
    path('<str:slug>/subscriptions/', Subscriptions.as_view()),
    path('<str:slug>/friends/', Friends.as_view()),
    path('<str:slug>/block/', BlackList.as_view(), name='blacklist_url'),


    path('<str:slug>/api/', APIUserProfile.as_view(), ),
    path('me/settings/api/', APIProfileSettings.as_view(), ),
    path('subscribers/<int:id>api/', APISubscribersList.as_view(),),
    path('subscriptions/<int:id>api/', APISubscriptionsList.as_view(), ),
    path('friends/<int:id>api/', APIFriendsList.as_view(), ),
    path('blacklist/api/', APIBlackList.as_view(), ),








]