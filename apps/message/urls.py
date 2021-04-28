from django.urls import path
from .views import *


urlpatterns = [
    path('api/', APIChatsList.as_view(), name='chat_list_url'),
    path('new/api/', APICreateChat.as_view(), name='create_chat_url'),
    path('id=<int:id>/api/', APIPrivateChat.as_view(), name='private_chat_url'),
    path('chat=<int:id>/api/', APIPublicChat.as_view(), name='public_chat_url'),
    path('chat=<int:id>/edit/api/', APIEditPublicChat.as_view(), name='edit_chat_url'),
    path('msg=<int:id>/api/', APIMessage.as_view(), name='messages_url')



    # path('', MessagesLit.as_view(), name='chat_list_url'),
    # path('new/', CreateChat.as_view(), name='create_chat_url'),
    # path('id=<int:id>/', PrivateChat.as_view(), name='private_chat_url'),
    # path('chat=<int:id>/', PublicChat.as_view(), name='public_chat_url'),
    # path('chat/delete/', DeleteChat.as_view(), name='delete_chat_url'),
    #
    # path('msg/', SendMessage.as_view(), name='messages_url'),
    # path('msg/delete/', DeleteMessage.as_view(), name='del_msg_url'),
    # path('msg/update/', UpdateMessage.as_view(), name='upd_msg_url'),
    # path('message/resend/'),



]