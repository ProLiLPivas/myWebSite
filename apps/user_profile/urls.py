from django.urls import path
from .views import *


urlpatterns = [
    # path('all'),
    path('me/', MyProfile.as_view(), name='get_my_profile'),
    path('update/', UpdateProfile.as_view(), name='update_profile'),
    path('<str:slug>/', UserProfile.as_view(), name='get_user_url'),

    path('<str:slug>/sub', subscribe, name='subscribe'),
    path('<str:slug>/add', add2friends, name='add_friend'),
    path('<str:slug>/unsub', unsubscribe, name='unsubscribe'),
    path('<str:slug>/remove', remove, name='remove_friend'),
    # path('<str:slug>/block', block, name='remove_friend'),
    # path('<str:slug>/unblock', unblock, name='remove_friend'),

    # path('<str:slug>/friends'),
    # path('<str:slug>/subs/', ),
    # path('<str:slug>/subs/', ),



]