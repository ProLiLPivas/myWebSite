from django.shortcuts import render, redirect
from django.views import View

from .utils import *


class MessageView(View):
    ''' '''
    def get(self, request, chat_id):

        if request.is_ajax():
            chat = Chat.objects.get(id=chat_id)
            messages_dict, users_dict, chat_dict = ChatUtils.gen_chat_data(chat)
            return JsonResponse({'messages': messages_dict, 'users': users_dict, 'chat': chat_dict}, status=200)

    def post(self, request, chat_id):

        request.POST['user'] = request.user
        request.POST['chat'] = Chat.objects.get(id=chat_id)
        new_message = MessageUtils.create_or_update_message(request.POST)
        if new_message:
            return JsonResponse({'new_message': model_to_dict(new_message)})
        else:
            return HttpResponse(status=403)


class UpdateMessage(View):
    def post(self, request):

        request.POST['user'] = request.user
        msg_instance = Message.objects.get(id=request.POST['message_id'])
        updated_message = MessageUtils.create_or_update_message(request.POST, instance=msg_instance)

        if updated_message:
            return JsonResponse({'new_message':  model_to_dict(updated_message)})
        else:
            return HttpResponse(status=403)

class DeleteMessage(View):
    def post(self, request):

        chat = Chat.objects.get(id=request.POST['chat_id'])
        messages = MessageUtils.parseId_and_gen_request(request.POST['chosenMessages'])
        role = Connection2Chat.objects.get(user=request.user, chat=chat).role

        for message in messages:
            if message.from_user == request.user or chat.del_messages <= role:
                message.delete()

            return JsonResponse({'is_del': 'ok'}, status=200)


class CreateChat(View):
    """  """
    friends = None
    template = 'message/chat_create.html'

    def get(self, request):

        friends = list(Relations.objects.filter(user_one__user=request.user, is_friends=1))
        friends_dict = [model_to_dict(friend) for friend in friends]

        if request.is_ajax():
            return JsonResponse({'user': request.user.id, 'friends': friends_dict}, status=200)

        return render(request, self.template)

    def post(self, request):

        friends = ChatUtils.parseId(request.POST['friends'])
        is_public = request.POST['is_public'] == 'true'
        chat_name = request.POST['chat_name']

        if is_public:
            chat = Chat.objects.create(id=chat_name, is_public=True)  # creating chat
            creator_connection = ChatUtils.generate_connections(user=request.user, chat=chat, role=3)
            for user_id in friends:
                ChatUtils.generate_connections(user=user_id, chat=chat)
        else:
            try:
                creator_connection = Connection2Chat.objects.get(user__id=request.user, recipient__id=int(friends[0]))
            except(Connection2Chat.DoesNotExist):
                creator_connection = ChatUtils.generate_connections(user=request.user, recipient=int(friends[0]))
        return redirect(creator_connection.get_chat_url())


class BaseChat:
    """This mixin we use 2 render"""
    is_public = None
    template = 'message/chat.html'
    chat_connection = None

    def get(self, request, id):

        data = {'connection': self.chat_connection}
        try:
            self.chat_connection = ChatUtils.get_private_or_public_chat(self.is_public, request.user, id)
            return render(request, self.template, context=data)
        except Connection2Chat.DoesNotExist:
            if not self.is_public:
                self.chat_connection = ChatUtils.generate_connections(request.user, recipient=id)
                return render(request, self.template, context=data)

    def post(self, request, id):

        c = ChatChanges()
        if request.POST['changes'] == 'add':
            return c.addUsers(request, id)
        elif request.POST['changes'] == 'kick':
            return c.removeUser(request, id)
        elif request.POST['changes'] == 'admin':
            return c.addRemoveAdmin(request, id)
        elif  request.POST['changes'] == 'name':
            return c.changeChatName(request, id)
        elif request.POST['changes'] == 'img':
            return c.changeChatImage(request, id)
        elif request.POST['changes'] == 'settings':
            return c.changeSettings(request, id)
        else:
            return HttpResponse(status=404)


class DeleteChat(View):
    def post(self, request, id):
        chat = Chat.objects.get(id=id)
        con = Connection2Chat.objects.get(chat__id=chat, user=request.user)
        if con.role == 3:
            chat.delete()
            return redirect('messages_list_url')
        else:
            return HttpResponse(status=403)


class PrivateChat(BaseChat, View):
    is_public = False


class PublicChat(BaseChat, View):
    is_public = True








