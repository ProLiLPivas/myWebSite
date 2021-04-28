from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.shortcuts import redirect
from rest_framework.response import Response

from .forms import *
from apps.user_profile.models import UsersRelation , Profile


def generate_private_chat_and_connections(user, second_user):
    connection = PrivateChatConnection.objects.filter(
        user=user, recipient=second_user).first()
    if not connection:
        second_user = User.objects.get(id=second_user)
        if not second_user.profile.is_messaging_accessible(user):
            return None
        chat = Chat.objects.create()
        PrivateChatConnection.objects.create(
            user=second_user, recipient=second_user, chat=chat)
        connection = PrivateChatConnection.objects.create(
            user=user, recipient=second_user, chat=chat)
    return connection


def generate_public_chat_and_connections(user, other_users, validate_data,):
        chat = Chat.objects.create(
            chat_name=validate_data.get('chat_name'), is_public=True)
        for user_id in other_users:
            chat_user = User.objects.get(id=user_id)
            if not chat_user.profile.is_messaging_accessible(user):
                return None
            PublicChatConnection.objects.create(user=chat_user, chat=chat)
        return PublicChatConnection.objects.create(
            user=user, chat=chat, role=3)


def removeUser(user, kicked_user_id, chat):
    your_connection = PublicChatConnection.objects.get(chat=chat , user=user)
    if kicked_user_id == user.id:
        Message.objects.create(
            chat=chat, text='{} leave_chat'.format(user), is_ancillary=True)
        if your_connection.role != 3:
            your_connection.delete()
            return Response(status=204)
        new_chat_leader = PublicChatConnection.objects.filter(
            chat=chat).order_by('role').first()
        new_chat_leader.role = 3
        new_chat_leader.save()
        return Response(status=204)
    your_role = your_connection.role
    kicked_user_connection = PublicChatConnection.objects.get(
        chat=chat, user=kicked_user_id)
    if kicked_user_connection.role < your_role and chat.remove_users <= your_role:
        kicked_user_connection.delete()
        text = '{} kick {}'.format(user, kicked_user_connection.user)
        Message.objects.create(
            chat=chat, text=text, is_ancillary=True)
        return Response(status=204)
    return Response(status=403)


def addUsers(user, other_users, chat):
    your_connection = PublicChatConnection.objects.get(chat=chat, user=user)
    if your_connection.role >= chat.add_new_users:
        users = other_users.split(',')
        for user_id in users:
            chat_user = User.objects.get(id=user_id)
            if chat_user.profile.is_messaging_accessible(user):
                PublicChatConnection.objects.get_or_create(
                    user=chat_user, chat=chat)
                text = '{} add {} to chat'.format(user, chat_user)
                Message.objects.create(
                    chat=chat, text=text, is_ancillary=True)
        return Response(status=201)
    return Response(status=403)


def addRemoveAdmin(user, user_id, chat):
    your_connection = PublicChatConnection.objects.get(chat=chat, user=user)
    if your_connection.role >= chat.add_remove_admins:
        con = ConnectionToChat.objects.get(user=user_id, chat=chat)
        if your_connection.role > con.role:
            if con.role == 1:
                con.role = 2
            elif con.role == 2:
                con.role = 1
            con.save()
            return Response(status=200)
    return Response(status=403)










def parseId_and_gen_request(text):
        q = Q()
        for message_id in text.split(','):
            q = q | Q(id=message_id)
        return Message.objects.filter(q)




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


def delete_message(data):

        pass

#chat utls

def get_chat_and_connection(chat_id, user):
        chat = Chat.objects.get(id=int(chat_id))
        con = ConnectionToChat.objects.get(chat=chat, user=user)
        return chat, con

def get_private_or_public_chat(is_public, user, identity):
        ''' '''
        if is_public:
            return ConnectionToChat.objects.get(user=user, chat_num=identity)
        else:
            return ConnectionToChat.objects.get(
                user=user, recipient__id=identity, chat__is_public=False)


def chats_to_list(user):
        chats_dict = []
        connections = ConnectionToChat.objects.filter(user=user)
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
                'url': connection.get_absolute_url(),
                'last_message_text': last_msg.text,
                'last_message_time': last_msg.time,
                'last_message_user': username,
            })
        return chats_dict


def generate_data_to_create_chat(user):
        friends_dict = []
        friends_list = list(
            UsersRelation.objects.filter(
                main_user_profile__user=user,
                is_friends=1
            )
        )
        for friend in friends_list:
            data = {
                'id': friend.secondary_user_profile.id,
                'username':  friend.secondary_user_profile.__str__(),
                'url': friend.secondary_user_profile.get_absolute_url(),
                'role': 1,
            }
            friends_dict.append(data)
        return friends_dict


def generate_connections(user, chat=None, recipient=None, role=1):

        if isinstance(user, int):
            user = User.objects.get(id=user)

        if chat:
            # all public chats have the own ID for chat members, so we need find latest pub_chat_id to make new on for new chat
            last_chat = ConnectionToChat.objects.filter(
                user=user, chat__is_public=True).order_by('chat_num').last()
            if last_chat == None:
                num = 1
            else:
                num = last_chat.chat_num + 1
            return ConnectionToChat.objects.create(user=user, chat=chat, chat_num=num, role=role)
        else:
            if isinstance(recipient, int):
                recipient = User.objects.get(id=recipient)
            chat = Chat.objects.create()
            ConnectionToChat.objects.create(user=recipient, chat=chat, recipient=user, role=0)
            return ConnectionToChat.objects.create(user=user, chat=chat, recipient=recipient, role=0)


def gen_chat_data(chat):
        chat_dict = model_to_dict(chat)
        connections_list = list(ConnectionToChat.objects.filter(chat=chat))
        messages_list = list(Message.objects.filter(chat=chat))
        messages_dict = [model_to_dict(message_obj) for message_obj in messages_list]
        users_dict = [connection_to_dict(connection_obj) for connection_obj in connections_list]

        chat_dict['chat_image'] = None  # REWRITE IN MEDIA UPDATE
        return messages_dict, users_dict, chat_dict


def connection_to_dict(connection_obj):
        connection_dict = {
            'id': connection_obj.user.id,
            'username': connection_obj.user.username,
            'url': connection_obj.user.profile.get_absolute_url(),
            'role': connection_obj.role
        }
        return connection_dict



# chat chenges





def changeChatName(request):
        chat, con = get_chat_and_connection(request.POST['chat_id'], request.user)
        if con.role >= chat.change_chat_name:
            chat.chat_name = request.POST['new_name']
            chat.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=403)

def changeChatImage( request):
            pass

def changeSettings(request):
        chat, con = get_chat_and_connection(request.POST['chat_id'], request.user)

        bound_form = ChatSettingsForm(request.POST, instance=chat)
        # print(bound_form.errors)

        if bound_form.is_valid() and con.role == 3:
            bound_form.save()
            return JsonResponse({'is_changes': 'ok'}, status=200)
        else:
            return HttpResponse(status=418)
