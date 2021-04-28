from django.shortcuts import render, redirect
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.user_profile.views import APIFriendsList
from .utils import *
from .serializers import *


class APIBaseChat(APIView):

    is_public = None

    def get_queryset(self, request, id):
        if self.is_public:
            connection = PublicChatConnection.objects.filter(
                user=request.user, chat_num=id).first()
            if not connection:
                return None
        else:
            connection = PrivateChatConnection.objects.filter(
                user=request.user, recipient=id).first()
            if not connection:
                serializer = ChatsCreateSerializer(
                    context={
                        'user': request.user,
                        'users': str(id),
                    },
                    data={
                        'chat_name': None,
                        'chat_image': None,
                        'setting': {},
                    }
                )
                if serializer.is_valid():
                    connection = serializer.save()
        return connection.chat

    def get(self, request, id):
        queryset = self.get_queryset(request, id)
        serializer = ChatSerializer(queryset, context={'request': request})
        if not serializer.data.get('id'):
            return Response(status=404)
        return Response(serializer.data)

    def post(self, request, id):
        chat = self.get_queryset(request, id)
        if not chat.is_public:
            if not PrivateChatConnection.objects.get(chat=chat, user=id)\
                    .recipient.profile.is_messaging_accessible(request.user):
                return Response(status=403)
        context = {'chat': chat, 'user': request.user}
        serializer = CreateMessageSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(status=201)
        return Response(status=400)


class APIPrivateChat(APIBaseChat):
    is_public = False


class APIPublicChat(APIBaseChat):

    is_public = True
    a = {
        "settings": {
            "send_messages": 1,
            "del_messages": 2,
            "add_new_users": 1,
            "remove_users": 2,
            "add_remove_admins": 3,
            "see_admins": 1 ,
            "change_chat_name": 2,
            "change_chat_image": 2
        }
    }

    def patch(self, request, id):
        instance = self.get_queryset(request, id)
        role = PublicChatConnection.objects.get(
            chat=instance, user=request.user).role
        if request.data.get('settings') and role < 3:
            request.data.remove('settings')
        if request.data.get('chat_name') and role < instance.change_chat_name:
            request.data.remove('chat_name')
        if request.data.get('chat_image') and role < instance.change_chat_image:
            request.data.remove('chat_image')
        context = {'settings': request.data.get('settings')}
        serializer = ChatsCreateSerializer(
            instance=instance, data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(status=201)
        return Response(status=400)

    def delete(self, request, id):
        connection = PublicChatConnection.objects.get(
            user=request.user, chat_num=id)
        if connection.role == 3:
            connection.chat.delete()
            return Response(status=204)
        return Response(status=403)


class APIChatsList(APIView):
    def get(self, request):
        queryset = [
            con.chat for con in ConnectionToChat.objects.filter(user=request.user)]
        serializer = ChatsListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class APICreateChat(APIFriendsList):

    def post(self, request):
        context = {'user': request.user, 'users': request.data.get('users')}
        serializer = ChatsCreateSerializer(data=request.data, context=context)
        if serializer.is_valid():
            creator_connection = serializer.save()
            return redirect(creator_connection.get_absolute_url())
        return Response(status=400)

    # {"users": "2,4", "chat_name": "000"}


class APIEditPublicChat(APIFriendsList):

    def post(self, request, id):
        chat = Chat.objects.get(id=id)
        if request.data['changes'] == 'add':
            return addUsers(request.user, request.data['user_id'], chat)
        elif request.data['changes'] == 'remove':
            return removeUser(request.user, request.data['user_id'], chat)
        elif request.data['changes'] == 'admin':
            return addRemoveAdmin(request.user, request.data['user_id'], chat)


class APIMessage(APIView):

    def put(self, request, id):
        instance = Message.objects.get(id=id)
        if instance.from_user == request.user:
            serializer = CreateMessageSerializer(instance=instance, data=request.data)
            if serializer.is_valid():
                serializer.save(is_changed=True)
                return Response(status=201)
            return Response(status=400)
        return Response(status=403)

    def delete(self, request, id):
        instance = Message.objects.get(id=id)
        role = ConnectionToChat.objects.get(
            chat=instance.chat, user=request.user).role
        if not instance.from_user == request.user \
                or instance.chat.del_messages < role:
            return Response(status=403)
        instance.delete()
        return Response(status=204)







#
#
#
# class MessagesLit(View):
#     """if we click on the postcard at navbar this code gonna work,
#      here we can watch list of all messages we have sent,
#      * if we haven't send any message yet, we are redirected on page witch recommended us to  send new one * """
#     template = 'message/chat_list.html'
#
#     def get(self, request):
#
#         if request.is_ajax():
#             chats_dict = chats_to_list(request.user)
#
#             return JsonResponse({'chats': chats_dict}, status=200)
#         return render(request, self.template)
#
#
# class SendMessage(View):
#     ''' '''
#     def post(self, request):
#         new_message = create_message(request.POST, request.user.id)
#         if new_message:
#             return JsonResponse({'new_message': model_to_dict(new_message)})
#         else:
#             return HttpResponse(status=403)
#
#
# class UpdateMessage(View):
#     def post(self, request):
#
#         updated_message = update_message(
#             request.POST['text'], request.POST['message_id'], request.POST['user_id'])
#
#         if updated_message:
#             return JsonResponse({'new_message':  model_to_dict(updated_message)})
#         else:
#             return HttpResponse(status=403)
#
#
# class DeleteMessage(View):
#     def post(self, request):
#         chat, con = get_chat_and_connection(request.POST['chat_id'], request.user)
#         messages = parseId_and_gen_request(request.POST['chosenMessages'])
#
#         for message in messages:
#             if message.from_user == request.user or chat.del_messages <= con.role:
#                 message.delete()
#
#         return JsonResponse({'is_del': 'ok'}, status=200)
#


# class BaseChat:
#     """   """
#     is_public = None
#     template = 'message/chat.html'
#     chat_connection = None
#
#     def get(self, request, id):
#         try:
#             self.chat_connection = get_private_or_public_chat(self.is_public, request.user, id)
#             data = {'connection': self.chat_connection}
#             if request.is_ajax():
#                 messages_dict, users_dict, chat_dict = gen_chat_data(self.chat_connection.chat)
#                 return JsonResponse({'messages': messages_dict, 'users': users_dict, 'chat': chat_dict}, status=200)
#             return render(request, self.template, context=data)
#         except ConnectionToChat.DoesNotExist:
#             if not self.is_public:
#                 self.chat_connection = generate_connections(request.user, recipient=id)
#                 return render(request, self.template, context={'connection': self.chat_connection})
#
#
#     def post(self, request, id):
#
#         if request.POST['changes'] == 'add':
#             return addUsers(request)
#         elif request.POST['changes'] == 'kick':
#             return removeUser(request)
#         elif request.POST['changes'] == 'admin':
#             return addRemoveAdmin(request)
#         elif  request.POST['changes'] == 'name':
#             return changeChatName(request)
#         elif request.POST['changes'] == 'img':
#             return changeChatImage(request)
#         elif request.POST['changes'] == 'settings':
#             return changeSettings(request)
#         else:
#             return HttpResponse(status=404)
#
#
# class DeleteChat(View):
#     def post(self, request):
#         chat, con = get_chat_and_connection(request.POST['chat_id'], request.user)
#         if con.role == 3:
#             chat.delete()
#             return redirect('chat_list_url')
#         else:
#             return HttpResponse(status=403)
#
#
# class PrivateChat(BaseChat, View):
#     is_public = False
#
#
# class PublicChat(BaseChat, View):
#     is_public = True

#
# class CreateChat(View):
#     """  """
#     friends = None
#     template = 'message/chat_create.html'
#
#     def get(self, request):
#
#         if request.is_ajax():
#             friends_dict = generate_data_to_create_chat(request.user)
#             return JsonResponse({'user': request.user.id, 'friends': friends_dict}, status=200)
#         return render(request, self.template)
#
#     def post(self, request):
#         friends = request.POST['friends'].split(',')
#
#         if request.POST['is_public'] == 'true':
#             chat = Chat.objects.create(chat_name=request.POST['chat_name'], is_public=True)  # creating chat
#             creator_connection = generate_connections(user=request.user, chat=chat, role=3)
#             for user_id in friends:
#                 generate_connections(user=user_id, chat=chat)
#         else:
#             try:
#                 creator_connection = ConnectionToChat.objects.get(user=request.user, recipient__id=int(friends[0]))
#             except(ConnectionToChat.DoesNotExist):
#                 creator_connection = generate_connections(user=request.user, recipient=int(friends[0]))
#
#         creator_connection.chat.create_last_message(str(request.user.username) + ' star chat')
#         return redirect(creator_connection.get_chat_url(),  permanent=True)
