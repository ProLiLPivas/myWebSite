from django.urls import path
from .views import *


urlpatterns = [
    path('', MessagesLit.as_view(), name='messages_list_url'),
    path('new/', CreateChat.as_view(), name='create_chat_url'),
    path('id=<int:id>/', PrivateChat.as_view(), name='private_chat_url'),
    path('chat=<int:id>/', PublicChat.as_view(), name='public_chat_url'),
    # path('chat=<int:id>/settings', changeSettings, name='chat_settings_url'),


    path('chat/remove_user', removeUser, name='kick_user_url' ),
    path('chat/admin', addRemoveAdmin, name='chat_admin_url'),
    path('chat/change_name', changeChatName, name='change_chat_name_url' ),
    path('chat/delete/', removeChat, name='delete_chat_url'),

    path('message/delete/', DeleteMessage.as_view(), name='del_msg_url'),
    path('message/update/', UpdateMessage.as_view(), name='upd_msg_url'),
    # path('message/resend/'),

]