from django.views import View

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.user_profile.forms import ProfileSettingsForm #
from apps.user_profile.utils.profile_utils import *  #
from apps.user_profile.utils.relations_mixixns import RelatedUsersView #
from apps.posts.utils.post_mixins import FeedMixin  #
from .serializers import *


class MyProfile(View):
    def get(self, request):
        return redirect(request.user.profile.get_absolute_url())


class APIUserProfile(APIView):
    def get(self, request, slug):
        queryset = Profile.objects.filter(slug=slug)
        serializer = ProfileSerializer(queryset , many=True,
                                    context={'request': request})
        return Response(serializer.data)

    def post(self, request, slug):
        if slug != request.user.profile.slug:
            if change_relations_status(slug, request.user.profile):
                return Response(200)
        return Response(403)

    def patch(self, request, slug=None):
        if slug == request.user.profile.slug:
            isinstance = Profile.objects.get(user=request.user)
            serializer = EditProfileSerializer(instance=isinstance , data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(status=200)
            return Response(status=400)
        return Response(status=403)


class APIProfileSettings(APIView):

    def get(self, request):
        queryset = Profile.objects.get(user=request.user)
        serializer = ProfileSettingsSerializer(queryset)
        return Response(serializer.data)

    def put(self, request):
        queryset = Profile.objects.get(user=request.user)
        serializer = ProfileSettingsSerializer(instance=queryset, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=200)
        return Response(status=400)


class BaseRelatedUsersView(APIView):

    queryset = None
    get_query_set_method = None

    def get_query_set(self, request=None, id=None):
        if self.get_query_set_method:
            self.get_query_set_method(request, id)

    def get(self, request, id=None):
        if not id:
            id = request.user.id
        self.get_query_set(request=request, id=id)
        serializer = RelatedUsersSerializer(
            self.queryset , many=True, context={'request': request})
        return Response(serializer.data)


class APIFriendsList(BaseRelatedUsersView):

    get_query_set_method = None

    def get_query_set(self, request=None, id=None):
        rel = UsersRelation.objects.filter(
            main_user_profile=id , is_friends=True)
        self.queryset = [r.secondary_user_profile for r in rel]


class APISubscribersList(BaseRelatedUsersView):

    get_query_set_method = None

    def get_query_set(self, request=None, id=None):
        rel = UsersRelation.objects.filter(
            secondary_user_profile=id, is_subscribed=True)
        self.queryset = [r.main_user_profile for r in rel]


class APISubscriptionsList(BaseRelatedUsersView):

    get_query_set_method = None

    def get_query_set(self, request=None, id=None):
        rel = UsersRelation.objects.filter(
            secondary_user_profile=id, is_subscribed=True)
        self.queryset = [r.main_user_profile for r in rel]


class APIBlackList(BaseRelatedUsersView):

    get_query_set_method = None

    def get_query_set(self, request=None, id=None):
        rel = UsersRelation.objects.filter(
            secondary_user_profile=request.user.id, is_blocked=True)
        self.queryset = [r.main_user_profile for r in rel]

class APIBlockUser(APIView):

    def post(self, request, id):
        if request.user.id == id:
            print(request.user.id)
            return Response({'ты': 'долбаеб?'}, status=400)
        relation_obj = UsersRelation.objects.get(
            main_user_profile=request.user.profile , secondary_user_profile=id)
        block_unblock_user(relation_obj)
        return Response(status=200)









class UserProfile(FeedMixin, View):
    template = 'profile/user_profile.html'
    query_parameters = ['user__profile__slug', None]
    
    def get(self, request, slug):
        if request.is_ajax():
            return FeedMixin.get(self, request, slug)
        else:
            context = get_profile_context(slug, request.user.profile, request.path)
            return render(request, self.template, context=context)


class ProfileSettings(View):
    def get(self, request):
        if request.is_ajax():
            data = {
                'access_messaging': request.user.profile.access_messaging,
                'access_posts': request.user.profile.access_posts,
                'access_about': request.user.profile.access_about,
                'access_albums': request.user.profile.access_albums,
                'access_images': request.user.profile.access_images,
                'access_stats': request.user.profile.access_stats,
            }
            return JsonResponse(data=data)
        return render(request, 'profile/profile_settings.html')

    def post(self, request):
        print(request.POST)
        bound_form = ProfileSettingsForm(request.POST, instance=request.user.profile)
        if bound_form.is_valid():
            bound_form.save()
            return redirect('/')



class ChangeAvatar:
    pass


class AddImage:
    pass


class ChangeProfileSettings:
    pass


class Subscriptions(RelatedUsersView, View):
    key = 'Subscriptions'
    slug_query_parameter = 'main_user_profile__slug'
    second_condition = ('is_subscribed', 1)
    is_have_post_method = False


class Subscribers(RelatedUsersView, View):
    key = 'Subscribers'
    slug_query_parameter = 'secondary_user_profile__slug'
    second_condition = ('is_subscribed', 1)
    post_action_func = subscribe_or_unsubscribe


class Friends(RelatedUsersView, View):
    key = 'Friends'
    slug_query_parameter = 'main_user_profile__slug'
    second_condition = ('is_friends', 1)
    post_action_func = add_or_remove_friends


class BlackList(RelatedUsersView, View):
    key = 'users in ur BlackList'
    slug_query_parameter = 'main_user_profile__slug'
    second_condition = ('is_blocked', 1)
    post_action_func = block_unblock_user



