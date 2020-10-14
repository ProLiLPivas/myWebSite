import json
from time import time

from django.db.models import Q
from django.forms import model_to_dict
from django.http import JsonResponse
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
                messages_model = list(Message.objects.filter(chat_id=chat_connection.chat_id))
                messages_dict = [model_to_dict(message_obj) for message_obj in messages_model]
                return JsonResponse({'messages': messages_dict}, status=200)

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

            new_obj = bound_form.save(commit=False)
            new_obj.from_user = request.user
            new_obj.chat_id = chat
            message = bound_form.save()
            chat.last_message_id = message.id
            chat.message_amount += 1
            chat.save()
            return JsonResponse({'new_message': model_to_dict(message)})



class PrivateChat(BaseChat, View):
    is_public = False

class PublicChat(BaseChat, View):
    is_public = True


class CreateChat(View):
    """"""
    template = 'message/chat_create.html'
    def get(self, request):
        # we can send new messages only to ur friends, we get friends list to create form
        friends = Relations.objects.filter(user_one__user=request.user, is_friends=1)
        # and here we render this form
        return render(request, self.template, context={'user': request.user, 'friends': friends})

    def post(self, request):
        # here we get data (name of chat, list of chosen persons, e.t.c) via ajax from user and put it into variables
        chat_name = request.POST['chat_name']
        friends = self.parseId(request.POST['friends'])
        # we get list of members as string, we reformat it to list via
        # the ways of making public and private chats are different, so amount of recipients collates on user side
        # and sends to us as is_public=True if amount of chat mates is bigger than 2

        if request.POST['is_public'] == 'true':

            chat = Chat(chat_name=chat_name, is_public=True, user_amount=len(friends)+1)
            chat.save() # creating chat
            chat_num = self.generate_public_chat_id(request.user)# get chat_num
            # now we have can create a connector object for chat creator and save it in database
            creator_connection = Connection2Chat(user=request.user, chat_id=chat, chat_num=chat_num)
            creator_connection.save()
            # after that we do the same for all chat members
            for user in friends:
                chat_num = self.generate_public_chat_id(user)
                Connection2Chat(user=User.objects.get(id=user), chat_id=chat, chat_num=chat_num).save()
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
                return redirect( creator_connection.get_chat_url())


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
                id_list.append(id)
                id = ''
        id_list.append(id)
        return id_list


class DeleteMessage(View):
    def post(self, request):
        # if user == post_user_id.....     # checking that user deleting this post is creator or admin

        messages = self.parseId(request.POST['chosenMessages'])
        chat = Chat.objects.get(id=request.POST['chat_id'])
        chat.message_amount -= len(messages)
        chat.save()
        messages.delete()

        return JsonResponse({'is_del': 'u gay'})


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
        new_text = request.POST['new_text']
        bound_form = MessageForm({'text': new_text}, instance=msg_obj)
        if bound_form.is_valid():
            bound_form.save()
            return JsonResponse({'text': new_text})


class ResendMessage:
    pass


def addUser():
    pass

def removeUser():
    pass

def addAdmin():
    pass

def removeAdmin():
    pass