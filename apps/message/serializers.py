from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.shortcuts import redirect

from rest_framework import serializers

from apps.user_profile.models import UsersRelation
from apps.posts.serializers import UserSerializer
from .utils import generate_private_chat_and_connections, \
    generate_public_chat_and_connections
from .forms import *
from .models import *


class ChatUserSerializer(UserSerializer):

    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'url', 'avatar', 'role')

    def get_role(self, obj: User):
        if self.context.get('chat'):
            if self.context['chat'].is_public:
                if not self.context.get('roles'):
                    return ConnectionToChat.objects.get(
                        user=obj, chat=self.context['chat']).role
                return self.context.get('roles').get(obj)
            return 0
        return


class ChatSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = (
            'send_messages',
            'del_messages',
            'add_new_users',
            'remove_users',
            'add_remove_admins',
            'see_admins',
            'change_chat_name',
            'change_chat_image',
        )


class MessageSerializer(serializers.ModelSerializer):

    from_user = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = '__all__'

    def get_from_user(self, obj: Message):
        return ChatUserSerializer(obj.from_user, context=self.context).data

class CreateMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ('text',)

    def create(self, validate_data):
        return Message.objects.create(
            from_user=self.context.get('user'),
            chat=self.context.get('chat'),
            text=validate_data.get('text'),
        )




class ChatSerializer(serializers.ModelSerializer):

    users = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()
    settings = serializers.SerializerMethodField()
    chat_name = serializers.SerializerMethodField()
    chat_image = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ('id', 'is_public', 'chat_name', 'chat_image', 'users',
            'messages', 'message_amount', 'user_amount', 'settings',)


    def get_users(self, obj: Chat):
        roles = dict(set(([(con.user, con.role) for con in
                           ConnectionToChat.objects.filter(chat=obj)])))
        return ChatUserSerializer(
                roles.keys(), many=True, context={'chat': obj, 'roles': roles}
        ).data

    def get_messages(self, obj: Chat):
        queryset = Message.objects.filter(chat=obj)
        return \
            MessageSerializer(queryset, many=True, context={'chat': obj}).data

    def get_chat_image(self, obj: Chat):
        if not obj.is_public:
            return
        if obj.chat_image:
            return obj.chat_image
        return

    def get_chat_name(self, obj: Chat):
        if not obj.is_public:
            return
        return obj.chat_name

    def get_settings(self, obj: Chat):
        return ChatSettingsSerializer(obj).data


class ChatsListSerializer(ChatSerializer):

    last_message = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ('id', 'chat_name', 'chat_image', 'url', 'last_message',)

    def get_last_message(self, obj: Chat):
        return MessageSerializer(obj.get_last_message()).data

    def get_url(self, obj: Chat):
        return ConnectionToChat.objects.get(
            chat=obj, user=self.context['request'].user).get_absolute_url()


class ChatsCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chat
        fields = ('chat_name', 'chat_image', 'send_messages', 'del_messages',
                'add_remove_admins', 'see_admins',
                'change_chat_name', 'change_chat_image',)

    def create(self, validate_data):
        users = self.context.get('users').split(',')

        if len(users) == 1:
            creator_connection = generate_private_chat_and_connections(
                self.context.get('user'), users[0])
        else:
            validate_data.update(self.context.get('settings', {}))
            creator_connection = generate_public_chat_and_connections(
                self.context.get('user'), users, validate_data)

        return creator_connection

    def update(self, instance, validate_data):
        validate_data.update(self.context.get('settings', {}))
        print(validate_data)
        return super().update(instance, validate_data)







#
#
# def parseId_and_gen_request(text):
#         q = ''
#         id_list = text.split(',')
#
#         for message_id in id_list:
#             if q == '':
#                 q = Q(id=message_id)
#             else:
#                 q = q | Q(id=message_id)
#
#         messages = Message.objects.filter(q)
#         return messages
#
#
# def update_message(text, msg_id, user):
#         data = {'text': text}
#         instance = Message.objects.get(id=int(msg_id))
#
#         bound_form = MessageUpdateForm(data, instance=instance)
#         if bound_form.is_valid():
#             if int(user) == instance.from_user.id:
#                 message = bound_form.save(commit=False)
#                 message.is_changed = True
#                 message.save()
#                 return message
#             return None
#
#
# def create_message(data, user):
#
#         chat_id = int(data['chat'])
#         data_dict = {
#             'text': data['text'],
#             'is_ancillary': data['is_ancillary'] == 'true',
#             'chat': chat_id,
#             'from_user': user
#         }
#
#         bound_form = MessageForm(data_dict)
#         if bound_form.is_valid():
#             message = bound_form.save()
#             chat = Chat.objects.get(id=chat_id)
#             chat.last_message_id = message.id
#             chat.save()
#             return message
#         return None
#
#
# def delete_message(data):
#
#         pass
#
# #chat utls
#
# def get_chat_and_connection(chat_id, user):
#         chat = Chat.objects.get(id=int(chat_id))
#         con = ConnectionToChat.objects.get(chat=chat, user=user)
#         return chat, con
#
# def get_private_or_public_chat(is_public, user, identity):
#         ''' '''
#         if is_public:
#             return ConnectionToChat.objects.get(user=user, chat_num=identity)
#         else:
#             return ConnectionToChat.objects.get(
#                 user=user, recipient__id=identity, chat__is_public=False)
#
#
# def chats_to_list(user):
#         chats_dict = []
#         connections = ConnectionToChat.objects.filter(user=user)
#         for connection in connections:
#             name = connection.chat.chat_name
#             if not name:
#                 name = connection.recipient.username
#                 user_url = connection.recipient.profile.get_absolute_url()
#             else:
#                 user_url = None
#
#             last_msg = Message.objects.get(id=connection.chat.last_message_id)
#
#             if not last_msg.from_user:
#                 username = ''
#             else:
#                 username = last_msg.from_user.username
#
#             chats_dict.append({
#                 'id': connection.chat.id,
#                 'name': name,
#                 'user_url': user_url,
#                 'url': connection.get_absolute_url(),
#                 'last_message_text': last_msg.text,
#                 'last_message_time': last_msg.time,
#                 'last_message_user': username,
#             })
#         return chats_dict
#
#
# def generate_data_to_create_chat(user):
#         friends_dict = []
#         friends_list = list(
#             UsersRelation.objects.filter(
#                 main_user_profile__user=user,
#                 is_friends=1
#             )
#         )
#         for friend in friends_list:
#             data = {
#                 'id': friend.secondary_user_profile.id,
#                 'username':  friend.secondary_user_profile.__str__(),
#                 'url': friend.secondary_user_profile.get_absolute_url(),
#                 'role': 1,
#             }
#             friends_dict.append(data)
#         return friends_dict
#
#
# def generate_connections(user, chat=None, recipient=None, role=1):
#
#         if isinstance(user, int):
#             user = User.objects.get(id=user)
#
#         if chat:
#             # all public chats have the own ID for chat members, so we need find latest pub_chat_id to make new on for new chat
#             last_chat = ConnectionToChat.objects.filter(user=user, chat__is_public=True).order_by('chat_num').last()
#             if last_chat == None:
#                 num = 1
#             else:
#                 num = last_chat.chat_num + 1
#             return ConnectionToChat.objects.create(user=user, chat=chat, chat_num=num, role=role)
#         else:
#             if isinstance(recipient, int):
#                 recipient = User.objects.get(id=recipient)
#             chat = Chat.objects.create()
#             ConnectionToChat.objects.create(user=recipient, chat=chat, recipient=user, role=0)
#             return ConnectionToChat.objects.create(user=user, chat=chat, recipient=recipient, role=0)
#
#
# def gen_chat_data(chat):
#         chat_dict = model_to_dict(chat)
#         connections_list = list(ConnectionToChat.objects.filter(chat=chat))
#         messages_list = list(Message.objects.filter(chat=chat))
#         messages_dict = [model_to_dict(message_obj) for message_obj in messages_list]
#         users_dict = [connection_to_dict(connection_obj) for connection_obj in connections_list]
#
#         chat_dict['chat_image'] = None  # REWRITE IN MEDIA UPDATE
#         return messages_dict, users_dict, chat_dict
#
#
# def connection_to_dict(connection_obj):
#         connection_dict = {
#             'id': connection_obj.user.id,
#             'username': connection_obj.user.username,
#             'url': connection_obj.user.profile.get_absolute_url(),
#             'role': connection_obj.role
#         }
#         return connection_dict
#
#
#
# # chat chenges
#
# def addUsers(request):
#         data = []
#         id = int(request.POST['chat_id'])
#         chat = Chat.objects.get(id=id)
#         friends = request.POST['friends'].split(',')
#         for user_id in friends:
#             connection = generate_connections(user=user_id, chat=chat)
#             data.append(connection_to_dict(connection))
#         return JsonResponse({'new_users': data})
#
# def removeUser(request):
#         chat, con = get_chat_and_connection(request.POST['chat_id'], request.user)
#         kicked_user_id = int(request.POST['user_id'])
#         if kicked_user_id == request.user.id or con.role >= chat.remove_users:
#             ConnectionToChat.objects.get(user__id=kicked_user_id, chat=chat).delete()
#             if kicked_user_id == request.user.id:
#                 return redirect('messages_list_url')
#             return HttpResponse(status=200)
#         else:
#             return HttpResponse(status=403)
#
# def addRemoveAdmin(request):
#         chat, your_con = get_chat_and_connection(request.POST['chat_id'], request.user)
#         if your_con.role >= chat.add_remove_admins:
#             con =  ConnectionToChat.objects.get(user__id=int(request.POST['user_id']), chat=chat)
#             if con.role == 1:
#                 role, con.role = 2, 2
#             elif con.role == 2:
#                 role, con.role = 1, 1
#             else:
#                 return HttpResponse(status=403)
#             con.save()
#             return JsonResponse({'role': role}, status=200)
#         else:
#             return HttpResponse(status=403)
#
# def changeChatName(request):
#         chat, con = get_chat_and_connection(request.POST['chat_id'], request.user)
#         if con.role >= chat.change_chat_name:
#             chat.chat_name = request.POST['new_name']
#             chat.save()
#             return HttpResponse(status=200)
#         else:
#             return HttpResponse(status=403)
#
# def changeChatImage( request):
#             pass
#
# def changeSettings(request):
#         chat, con = get_chat_and_connection(request.POST['chat_id'], request.user)
#
#         bound_form = ChatSettingsForm(request.POST, instance=chat)
#         # print(bound_form.errors)
#
#         if bound_form.is_valid() and con.role == 3:
#             bound_form.save()
#             return JsonResponse({'is_changes': 'ok'}, status=200)
#         else:
#             return HttpResponse(status=418)
