from django.urls import path
from apps.relations.views import Friends, Subs, Search

urlpatterns = [
    path('', Friends.as_view(), name='friends_url' ),
    # path('?id=<int:id>' , Friends.as_view(), ) ,
    path('subs/', Subs.as_view(), name='subs_url'),
    # path('/subs/?id=<int:id>',),
    path('search/', Search.as_view(), name='search_url'),
]