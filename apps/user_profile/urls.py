from django.urls import path
from .views import *


urlpatterns = [
    # path('all'),
    path('friends/', Friends.as_view(), name='friends_url'),
    path('subs/', Subs.as_view(), name='subs_url'),
    path('search/', Search.as_view(), name='search_url'),

    path('me/', MyProfile.as_view(), name='get_my_profile'),
    path('update/', UpdateProfile.as_view(), name='update_profile'),

    path('<str:slug>/', UserProfile.as_view(), name='get_user_url'),

    path('<str:slug>/sub', subscribe, name='subscribe'),
    path('<str:slug>/add', add2friends, name='add_friend'),
    path('<str:slug>/unsub', unsubscribe, name='unsubscribe'),
    path('<str:slug>/remove', remove, name='remove_friend'),
    # path('<str:slug>/block', block, name='remove_friend'),
    # path('<str:slug>/unblock', unblock, name='remove_friend'),





]