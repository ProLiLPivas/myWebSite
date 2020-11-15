from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.shortcuts import redirect

from .forms import *


class MessageUtils:

    @staticmethod
    def parseId_and_gen_request(text):
        q = ''
        id_list = ChatUtils.parseId(text)

        for message_id in id_list:
            if q == '':
                q = Q(id=message_id)
            else:
                q = q | Q(id=message_id)

        messages = Message.objects.filter(q)
        return messages

    @staticmethod               # slit them
    def  update_message (text, msg_id, user):
        data = {'text': text}
        instance = Message.objects.get(id=int(msg_id))

        bound_form = MessageUpdateForm(data, instance=instance)
        if bound_form.is_valid():
            if int(user) == instance.from_user.id:
                message = bound_form.save(commit=False)
                message.is_changed = True
                message.save()
                return message
            return None

    @staticmethod
    def create_message(data, user):

        chat_id = int(data['chat'])
        data_dict = {
            'text': data['text'],
            'is_ancillary': data['is_ancillary'] == 'true',
            'chat': chat_id,
            'from_user': user
        }

        bound_form = MessageForm(data_dict)
        if bound_form.is_valid():
            message = bound_form.save()
            chat = Chat.objects.get(id=chat_id)
            chat.last_message_id = message.id
            chat.save()
            return message
        return None

    @staticmethod
    def delete_message(data):

        pass


class ChatUtils:
    @staticmethod
    def get_chat_and_connection(chat_id, user):
        chat = Chat.objects.get(id=int(chat_id))
        con = Connection2Chat.objects.get(chat=chat, user=user)
        return chat, con

    @staticmethod
    def get_private_or_public_chat(is_public, user, identity):
        ''' '''
        if is_public:
            return Connection2Chat.objects.get(user=user, chat_num=identity)
        else:
            return Connection2Chat.objects.get(user=user, recipient__id=identity, chat__is_public=False)

    @staticmethod
    def chats_to_list(user):
        chats_dict = []
        connections = Connection2Chat.objects.filter(user=user)
        for connection in connections:
            name = connection.chat.chat_name
            if not name:
                name = connection.recipient.username
                user_url = connection.recipient.profile.get_absolute_url()
            else:
                user_url = None

            last_msg = Message.objects.get(id=connection.chat.last_message_id)

            if not last_msg.from_user:
                username = ''
            else:
                username = last_msg.from_user.username

            chats_dict.append({
                'id': connection.chat.id,
                'name': name,
                'user_url': user_url,
                'url': connection.get_chat_url(),
                'last_message_text': last_msg.text,
                'last_message_time': last_msg.time,
                'last_message_user': username,
            })
        return chats_dict

    @staticmethod
    def generate_data_to_create_chat(user):
        friends_dict = []
        friends_list = list(Relations.objects.filter(user_one__user=user, is_friends=1))
        for friend in friends_list:
            data = {
                'id': friend.user_two.id,
                'username':  friend.user_two.__str__(),
                'url': friend.user_two.get_absolute_url(),
                'role': 1,
            }
            friends_dict.append(data)
        return friends_dict

    @staticmethod
    def generate_connections(user, chat=None, recipient=None, role=1):

        if isinstance(user, int):
            user = User.objects.get(id=user)

        if chat:
            # all public chats have the own ID for chat members, so we need find latest pub_chat_id to make new on for new chat
            last_chat = Connection2Chat.objects.filter(user=user, chat__is_public=True).order_by('chat_num').last()
            if last_chat == None:
                num = 1
            else:
                num = last_chat.chat_num + 1
            return Connection2Chat.objects.create(user=user, chat=chat, chat_num=num, role=role)
        else:
            if isinstance(recipient, int):
                recipient = User.objects.get(id=recipient)
            chat = Chat.objects.create()
            Connection2Chat.objects.create(user=recipient, chat=chat, recipient=user, role=0)
            return Connection2Chat.objects.create(user=user, chat=chat, recipient=recipient, role=0)

    @staticmethod
    def gen_chat_data(chat):
        chat_dict = model_to_dict(chat)
        connections_list = list(Connection2Chat.objects.filter(chat=chat))
        messages_list = list(Message.objects.filter(chat=chat))
        messages_dict = [model_to_dict(message_obj) for message_obj in messages_list]
        users_dict = [ChatUtils.connection_to_dict(connection_obj) for connection_obj in connections_list]

        chat_dict['chat_image'] = None  # REWRITE IN MEDIA UPDATE
        return messages_dict, users_dict, chat_dict

    @staticmethod
    def connection_to_dict(connection_obj):
        connection_dict = {
            'id': connection_obj.user.id,
            'username': connection_obj.user.username,
            'url': connection_obj.user.profile.get_absolute_url(),
            'role': connection_obj.role
        }
        return connection_dict

    @staticmethod
    def parseId(text):

        id, id_list = '', []
        for symbol in text:
            if not symbol == ',':
                id += symbol
            else:
                id_list.append(int(id))
                id = ''
        id_list.append(int(id))
        return id_list


class ChatChanges():

    def addUsers(self, request):
        data = []
        id = int(request.POST['chat_id'])
        chat = Chat.objects.get(id=id)
        friends = ChatUtils.parseId(request.POST['friends'])
        for user_id in friends:
            connection = ChatUtils.generate_connections(user=user_id, chat=chat)
            data.append(ChatUtils.connection_to_dict(connection))
        return JsonResponse({'new_users': data})

    def removeUser(self, request):
        chat, con = ChatUtils.get_chat_and_connection(request.POST['chat_id'], request.user)
        kicked_user_id = int(request.POST['user_id'])
        if kicked_user_id == request.user.id or con.role >= chat.remove_users:
            Connection2Chat.objects.get(user__id=kicked_user_id, chat=chat).delete()
            if kicked_user_id == request.user.id:
                return redirect('messages_list_url')
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=403)

    def addRemoveAdmin(self, request):
        chat, your_con = ChatUtils.get_chat_and_connection(request.POST['chat_id'], request.user)
        if your_con.role >= chat.add_remove_admins:
            con =  Connection2Chat.objects.get(user__id=int(request.POST['user_id']), chat=chat)
            if con.role == 1:
                role, con.role = 2, 2
            elif con.role == 2:
                role, con.role = 1, 1
            else:
                return HttpResponse(status=403)
            con.save()
            return JsonResponse({'role': role}, status=200)
        else:
            return HttpResponse(status=403)

    def changeChatName(self, request):
        chat, con = ChatUtils.get_chat_and_connection(request.POST['chat_id'], request.user)
        if con.role >= chat.change_chat_name:
            chat.chat_name = request.POST['new_name']
            chat.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=403)

    def changeChatImage(self, request):
            pass

    def changeSettings(self,request):
        chat, con = ChatUtils.get_chat_and_connection(request.POST['chat_id'], request.user)

        bound_form = ChatSettingsForm(request.POST, instance=chat)
        print(bound_form.errors)

        if bound_form.is_valid() and con.role == 3:
            bound_form.save()
            return JsonResponse({'is_changes': 'ok'}, status=200)
        else:
            return HttpResponse(status=418)
