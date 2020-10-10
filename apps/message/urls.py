from django.urls import path
from .views import *


urlpatterns = [
    path('', MessagesLit.as_view(), name='messages_list_url'),
    path('new', CreateChat.as_view(), name='create_chat_url'),
    path('id=<int:id>', PrivateChat.as_view(), name='private_chat_url'),
    path('chat=<int:id>', PublicChat.as_view(), name='public_chat_url'),
    path('test', Test.as_view(), name='test_url')
]