from django.shortcuts import render, redirect
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.user_profile.views import APIFriendsList
from .utils import *
from .serializers import *

class APIBaseChat(APIView):

    second_query_parameter = None

    def get_queryset(self, request, id):
        second_query = Q((self.second_query_parameter, id))
        return Connection2Chat.objects.get(
            Q(('user', request.user)), second_query).chat

    def get(self, request, id):
        queryset = self.get_queryset(request, id)
        serializer = ChatSerializer(queryset, context={'request': request})
        return Response(serializer.data)




class APIPrivateChat(APIBaseChat):
    second_query_parameter = 'recipient'


class APIPublicChat(APIBaseChat):
    second_query_parameter = 'chat_num'


class APIChatsList(APIView):
    def get(self, request):
        queryset = [con.chat for con in Connection2Chat.objects.filter(user=request.user)]
        serializer = ChatsListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class APINewChat(APIFriendsList):

    def post(self, request):
        pass

class APIAddUserToChat(APIFriendsList):
    pass

class APIMessage(APIView):

    def post(self, request):
        pass

    def put(self, request):
        pass

    def delete(self, request):
        pass


class MessagesLit(View):
    """if we click on the postcard at navbar this code gonna work,
     here we can watch list of all messages we have sent,
     * if we haven't send any message yet, we are redirected on page witch recommended us to  send new one * """
    template = 'message/chat_list.html'

    def get(self, request):

        if request.is_ajax():
            chats_dict = chats_to_list(request.user)

            return JsonResponse({'chats': chats_dict}, status=200)
        return render(request, self.template)


class SendMessage(View):
    ''' '''
    def post(self, request):
        new_message = create_message(request.POST, request.user.id)
        if new_message:
            return JsonResponse({'new_message': model_to_dict(new_message)})
        else:
            return HttpResponse(status=403)


class UpdateMessage(View):
    def post(self, request):

        updated_message = update_message(
            request.POST['text'], request.POST['message_id'], request.POST['user_id'])

        if updated_message:
            return JsonResponse({'new_message':  model_to_dict(updated_message)})
        else:
            return HttpResponse(status=403)


class DeleteMessage(View):
    def post(self, request):
        chat, con = get_chat_and_connection(request.POST['chat_id'], request.user)
        messages = parseId_and_gen_request(request.POST['chosenMessages'])

        for message in messages:
            if message.from_user == request.user or chat.del_messages <= con.role:
                message.delete()

        return JsonResponse({'is_del': 'ok'}, status=200)



class BaseChat:
    """   """
    is_public = None
    template = 'message/chat.html'
    chat_connection = None

    def get(self, request, id):
        try:
            self.chat_connection = get_private_or_public_chat(self.is_public, request.user, id)
            data = {'connection': self.chat_connection}
            if request.is_ajax():
                messages_dict, users_dict, chat_dict = gen_chat_data(self.chat_connection.chat)
                return JsonResponse({'messages': messages_dict, 'users': users_dict, 'chat': chat_dict}, status=200)
            return render(request, self.template, context=data)
        except Connection2Chat.DoesNotExist:
            if not self.is_public:
                self.chat_connection = generate_connections(request.user, recipient=id)
                return render(request, self.template, context={'connection': self.chat_connection})


    def post(self, request, id):

        if request.POST['changes'] == 'add':
            return addUsers(request)
        elif request.POST['changes'] == 'kick':
            return removeUser(request)
        elif request.POST['changes'] == 'admin':
            return addRemoveAdmin(request)
        elif  request.POST['changes'] == 'name':
            return changeChatName(request)
        elif request.POST['changes'] == 'img':
            return changeChatImage(request)
        elif request.POST['changes'] == 'settings':
            return changeSettings(request)
        else:
            return HttpResponse(status=404)


class DeleteChat(View):
    def post(self, request):
        chat, con = get_chat_and_connection(request.POST['chat_id'], request.user)
        if con.role == 3:
            chat.delete()
            return redirect('chat_list_url')
        else:
            return HttpResponse(status=403)


class PrivateChat(BaseChat, View):
    is_public = False


class PublicChat(BaseChat, View):
    is_public = True


class CreateChat(View):
    """  """
    friends = None
    template = 'message/chat_create.html'

    def get(self, request):

        if request.is_ajax():
            friends_dict = generate_data_to_create_chat(request.user)
            return JsonResponse({'user': request.user.id, 'friends': friends_dict}, status=200)
        return render(request, self.template)

    def post(self, request):
        friends = request.POST['friends'].split(',')

        if  request.POST['is_public'] == 'true':
            chat = Chat.objects.create(chat_name=request.POST['chat_name'], is_public=True)  # creating chat
            creator_connection = generate_connections(user=request.user, chat=chat, role=3)
            for user_id in friends:
                generate_connections(user=user_id, chat=chat)
        else:
            try:
                creator_connection = Connection2Chat.objects.get(user=request.user, recipient__id=int(friends[0]))
            except(Connection2Chat.DoesNotExist):
                creator_connection = generate_connections(user=request.user, recipient=int(friends[0]))

        creator_connection.chat.create_last_message(str(request.user.username) + ' star chat')
        return redirect(creator_connection.get_chat_url(),  permanent=True)
