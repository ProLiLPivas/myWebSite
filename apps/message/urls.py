from django.urls import path
from .views import *


urlpatterns = [
    path('', MessagesLit.as_view(), name='messages_list_url'),
    path('new/', CreateChat.as_view(), name='create_chat_url'),
    path('id=<int:id>/', PrivateChat.as_view(), name='private_chat_url'),
    path('chat=<int:id>/', PublicChat.as_view(), name='public_chat_url'),

    # path('chat/delete/'),
    # path('chat/add_user'),
    # path('chat/remove_user'),
    # path('chat/add_admin'),
    # path('chat/remove_admin'),
    # path('chat/change'),

    path('message/delete/', DeleteMessage.as_view(), name='del_msg_url'),
    path('message/update/', UpdateMessage.as_view(), name='upd_msg_url'),
    # path('message/resend/'),

]