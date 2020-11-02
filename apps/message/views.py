import json
from time import time

from django.db.models import Q
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from apps.relations.models import Relations
from .forms import MessageForm, ChatForm
from .models import *


class MessagesLit(View):
    """if we click on the postcard at navbar this code gonna work,
     here we can watch list of all messages we have sent,
     * if we haven't send any message yet, we are redirected on page witch recommended us to  send new one * """
    template = 'message/messages_list.html'
    def get(self, request):
       # here we get from db all connection to chats that we have
        # and if we don't find any chat, user will pres hte button which redirect him to create chat form
        chats = Connection2Chat.objects.filter(user=request.user)
        return render(request, self.template, context={'user': request.user, 'chats': chats, })

class BaseChat:
    """This mixin we use 2 render"""
    is_public = None
    model_form = MessageForm

    template = 'message/chat.html'
    form = model_form()

    def get_private_or_public_chat(self, user, identity):
        if self.is_public:
            return Connection2Chat.objects.get(user=user, chat_num=identity)
        else:
            return Connection2Chat.objects.get(user=user, recipient__id=identity, chat_id__is_public=False)

    def get(self, request, id):
        try:
            chat_connection = self.get_private_or_public_chat(request.user, id)
            if request.is_ajax():
                chat = chat_connection.chat_id
                messages_list = list(Message.objects.filter(chat_id=chat))
                messages_dict = [model_to_dict(message_obj) for message_obj in messages_list]
                if self.is_public:
                    connections_list = list(Connection2Chat.objects.filter(chat_id=chat))
                    users_dict = [{
                        'id': con_obj.user.id,
                        'username':con_obj.user.username,
                        'role': con_obj.role,
                        'url': con_obj.get_chat_url()
                    } for con_obj in connections_list]
                else:
                    users_dict = []
                chat = model_to_dict(chat)
                chat['chat_image'] = ''

                return JsonResponse({'messages': messages_dict, 'users': users_dict, 'chat': chat}, status=200)
            return render(request, self.template, context={'connection': chat_connection})

        except Connection2Chat.DoesNotExist:
            if not self.is_public:
                # and if we dont find it, we create new columns in db for 2 this users
                user1 = User.objects.get(id=request.user.id)
                user2 = User.objects.get(id=id)
                chat = Chat(chat_name='', chat_image='').save()
                chat_connection = Connection2Chat(user=user1, chat_id=chat, recipient=user2)
                chat_connection.save()
                Connection2Chat(user=user2, chat_id=chat, recipient=user1).save()
                return render(request, self.template, context={
                    'message': [], 'user': request.user, 'connection': chat_connection
                })
        except Message.DoesNotExist:
            chat_connection = self.get_private_or_public_chat(request.user, id)
            return render(request, self.template, context={
                'message': [], 'user': request.user, 'connection': chat_connection})


    def post(self, request, id):
        connection= self.get_private_or_public_chat(request.user, id)
        chat = connection.chat_id
        bound_form = self.model_form(request.POST)
        if bound_form.is_valid():
            if connection.role >= chat.send_messages:
                new_obj = bound_form.save(commit=False)
                new_obj.from_user = request.user
                new_obj.chat_id = chat
                message = bound_form.save()
                chat.last_message_id = message.id
                chat.message_amount += 1
                chat.save()

                return JsonResponse({'new_message': model_to_dict(message)})
            else: return HttpResponse(status=403)


class PrivateChat(BaseChat, View):
    is_public = False

class PublicChat(BaseChat, View):
    is_public = True




class CreateChat(View):
    """

    """
    template = 'message/chat_create.html'
    def get(self, request):
        # we can send new messages only to our's friends,so we get friends list to create form
        friends = list(Relations.objects.filter(user_one__user=request.user, is_friends=1))
        # here we serialize QuerySet to dict and send it via json
        friends_dict = [model_to_dict(friend) for friend in friends]

        if request.is_ajax():
            return JsonResponse({'user': request.user.id, 'friends': friends_dict}, status=200)
        # and here we render this template
        return render(request, self.template)

    def post(self, request):
        # here we get data (name of chat, list of chosen persons, e.t.c) via ajax from user and put it into variables
        chat_name = request.POST['chat_name']
        friends = self.parseId(request.POST['friends'])
        # we get list of members as string, we reformat it to list via
        # the ways of making public and private chats are different, so amount of recipients collates on user side
        # and sends to us as is_public=True if amount of chat mates is bigger than 2
        print( request.POST['is_public'])
        if request.POST['is_public'] == 'true':

            chat = Chat.objects.get_or_create(id=chat_name) # creating chat
            if chat[1] == True:
                chat[0].is_public =True
                chat[0].chat_name = chat_name
                chat[0].save()
            chat = chat[0]
            # now we can create a connector object for chat creator and save it in database
            creator_connection = Connection2Chat.objects.get_or_create(user=request.user, chat_id=chat)
            if creator_connection[1]:
                chat_num = self.generate_public_chat_id(request.user)  # get chat_num
                creator_connection = creator_connection[0]
                creator_connection.chat_num = chat_num
                creator_connection.role = 3
                creator_connection.save()
                for user in friends:
                    chat_num = self.generate_public_chat_id(user)
                    Connection2Chat(user=User.objects.get(id=user), chat_id=chat, chat_num=chat_num).save()

                print(1)
            else:
                data = []
                creator_connection = creator_connection[0]
                for user_id in friends:
                    chat_num = self.generate_public_chat_id(user_id)
                    user = User.objects.get(id=user_id)
                    Connection2Chat(user=user, chat_id=chat, chat_num=chat_num).save()
                    data.append({
                        'id': user_id,
                         'name': user.username,
                    })

                JsonResponse({'new_users': data}, status=200, safe=False)
            # after that we do the same for all chat members
            # when we made all connections to chat we redirected to this chat
            return redirect(creator_connection.get_chat_url())
        elif(request.POST['is_public'] == 'false'):
            recipient = User.objects.get(id=friends[0])
            try:
                connection = Connection2Chat.objects.get(user=request.user, recipient=recipient)
                return redirect(connection.get_chat_url())
            except(Connection2Chat.DoesNotExist):
                chat = Chat(is_public=False)
                chat.save()
                creator_connection = Connection2Chat(user=request.user, chat_id=chat, recipient=recipient)
                creator_connection.save()
                Connection2Chat(user=recipient, chat_id=chat, recipient=request.user).save()
                return redirect(creator_connection.get_chat_url())


    def generate_public_chat_id(self, user):
        # all public chats have the own ID for chat members, so we need find latest pub_chat_id to make new on for new chat
        last_chat = Connection2Chat.objects.filter(user=user, chat_id__is_public=True).order_by('chat_num').last()
        if last_chat == None: return 1
        else: return last_chat.chat_num + 1

    def parseId(self, text):
        id, id_list = '', []
        for symbol in text:
            if not symbol == ',':
                id += symbol
            else:
                id_list.append(int(id))
                id = ''
        id_list.append(int(id))
        return id_list


class DeleteMessage(View):
    def post(self, request):

        messages = self.parseId(request.POST['chosenMessages'])
        chat = Chat.objects.get(id=request.POST['chat_id'])
        role = Connection2Chat.objects.get(user=request.user, chat_id=chat).role
        for message in messages:
            if message.from_user == request.user or chat.del_messages <= role:
                message.delete()
        return JsonResponse({'is_del': 'ok'})


    def parseId(self, text):
            id, q, id_list = '', '', []
            for symbol in text:
                if not symbol == ',':
                    id += symbol
                else:
                    id_list.append(int(id))
                    id = ''
            id_list.append(int(id))
            for message_id in id_list:
                if q == '':
                    q = Q(id=message_id)
                else:
                    q = q | Q(id=message_id)
            messages = Message.objects.filter(q)
            return messages

class UpdateMessage(View):
    model = None
    model_form = None

    def post(self, request):
        msg_obj = Message.objects.get(id=request.POST['message_id'])
        if msg_obj.from_user == request.user:
            new_text = request.POST['new_text']
            bound_form = MessageForm({'text': new_text}, instance=msg_obj)
            if bound_form.is_valid():
                bound_form.save()
                return JsonResponse({'text': new_text})
        else: return HttpResponse(status=403)


class ResendMessage:
    pass



def removeUser(request):
    if request.method == 'POST':
        chat = Chat.objects.get(id=request.POST['chat_id'])
        con = Connection2Chat.objects.get(chat_id=chat, user=request.user)
        kicked_user_id = int(request.POST['user_id'])
        if kicked_user_id == request.user.id or con.role >= chat.remove_users:
            Connection2Chat.objects.get(user__id=kicked_user_id, chat_id=chat).delete()
            if kicked_user_id == request.user.id:
                return redirect('messages_list_url')
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=403)



def addRemoveAdmin(request):
    if request.method == 'POST':
        chat = Chat.objects.get(id=request.POST['chat_id'])
        if Connection2Chat.objects.get(chat_id=chat, user=request.user).role >= chat.add_remove_admins:
            user = request.POST['user_id']
            con = Connection2Chat.objects.get(user__id=user, chat_id=chat)
            if con.role == 1:
                role, con.role = 2, 2
            elif con.role == 2:
                role, con.role = 1, 1
            else:
                return HttpResponse(status=403)
            con.save()
            return JsonResponse({'role': role}, status=200)

def changeChatName(request):
    if request.method == 'POST':
        chat = Chat.objects.get(id=request.POST['chat_id'])
        if Connection2Chat.objects.get(chat_id=chat, user=request.user).role >= chat.change_chat_name:
            chat.chat_name = request.POST['new_name']
            chat.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=403)

def changeChatImage(request):
    pass

def changeSettings(request):
    pass

def removeChat(request):
    if request.method == 'POST':
        chat = Chat.objects.get(id=request.POST['chat_id'])
        con = Connection2Chat.objects.get(chat_id=chat, user=request.user)
        if con.role == 3:
            chat.delete()
            return redirect('messages_list_url')
        else:
            return HttpResponse(status=403)