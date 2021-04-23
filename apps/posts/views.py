from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import model_to_dict
from django.views.generic import View

from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import *

from apps.posts.utils.post_mixins import *

from .forms import *
from .models import *


class APIFeed(APIView):

    def get(self, request,):
        queryset = Post.objects.filter(user__id=1)

        serializer = FeedSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class APIPost(APIView):
    def get(self, request, id):
        queryset = Post.objects.filter(id=id)
        serializer = SinglePostSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class APIComments(APIView):
    def get(self, request, id):
        queryset = Comment.objects.filter(post=id)
        serializer = CommentsSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class APITags(APIView):
    def get(self, request):
        queryset = Tag.objects.all()
        serializer = TagsListSerializer(queryset, many=True,)
        return Response(serializer.data)


class APITag(APIView):
    def get(self, request, slug):
        queryset = Post.objects.filter(tag__slug=slug)
        serializer = FeedSerializer(queryset, context={'request': request})
        return Response(serializer.data)





class Feed(FeedMixin, View):
    template = 'posts/feed.html'


class MostPopularFeed(FeedMixin, View):
    template = 'posts/feed.html'
    ordering = ('-likes_amount', '-comments_amount')


class FilteredFeed(FeedMixin, View, LoginRequiredMixin):
    pass
# class FriendsFeed(FeedMixin, View, LoginRequiredMixin):
#     template = 'posts/feed.html'
#
#
# class SubscribersFeed(FeedMixin, View, LoginRequiredMixin):
#     template = 'posts/feed.html'
#
#
# class SubscriptionFeed(FeedMixin, View, LoginRequiredMixin):
#     template = 'posts/feed.html'


class FeedForProfile(FeedMixin, View):
    template = 'posts/feed.html'
    query_parameters = ['user__profile__slug', None]


class ReadPost(FeedMixin, View):  # read details about post
    template = 'posts/read_post.html'
    query_parameters = ['id', None]


class CreatePost(View, LoginRequiredMixin):
    model = Post
    model_form = PostForm

    def post(self, request):
        new_post = PostUtils.create_post(request.POST, request.user)
        tags = PostUtils.create_or_get_tags(request.POST['tags'], new_post)
        post_dict = model_to_dict(new_post)
        post_dict['tag'] = tags
        return JsonResponse({'post': post_dict}, status=200)


class UpdatePost(View, LoginRequiredMixin):
    model = Post
    model_form = PostForm

    def post(self, request):
        updated_post, status = PostUtils.update_post(request.POST, request.POST['post_id'], request.user)
        tags = PostUtils.create_or_get_tags(request.POST['tags'], updated_post)
        return JsonResponse({'tag': tags}, status=status)


class DeletePost(View, LoginRequiredMixin):
    def post(self, request):
        amount = PostUtils.del_post(request.POST['id'], request.user)
        if amount:
            return JsonResponse(amount, status=200)
        return HttpResponse(status=403)


class PostSettings(View, LoginRequiredMixin):
    def post(self, request):
        http_status = PostUtils.set_post_permissions(request.POST, request.user)
        return HttpResponse(status=http_status)


class Tags(View):
    def get(self, request):
        return render(request, 'posts/tegs_list.html', context={'tags': Tag.objects.all()})


class ReadTag(FeedMixin, View):
    template = 'posts/read_tag.html'
    ordering = ('-likes_amount', '-comments_amount')
    query_parameters = ['tag__title', None]



class LikePost(LikeMixin, LoginRequiredMixin, View):
    model = Post


class LikeComment(LikeMixin, LoginRequiredMixin, View):
    model = Comment


class Comments(View, LoginRequiredMixin):
    def get(self, request, id):
        comments = PostSerializer.comments_to_dict(id, request.user)
        return JsonResponse({'comments': comments}, status=200)

    def post(self, request, id):
        bound_form = CommentForm(request.POST)
        new_comment, status = PostUtils.create_comment(bound_form, request.user, id)
        if new_comment:
            return JsonResponse({'comment': new_comment}, status=status)
        else:
            return HttpResponse(status=status)


class UpdateComment(View, LoginRequiredMixin):
    def post(self, request):
        new_text, status = PostUtils.update_comment(request.POST['comment_id'], request.POST['new_text'], request.user)
        return JsonResponse({'text': new_text}, status=status)


class DeleteComment(View , LoginRequiredMixin):
    def post(self, request):
        amount = PostUtils.del_comment(request.POST['id'], request.POST['post_id'], request.user)
        if amount:
            return JsonResponse(amount, status=200)
        return HttpResponse(status=403)




# class Repost(View):
#     pass


# class DeleteTag(LoginRequiredMixin, DeleteObjectMixin, View):
#     model = Tag
#     template = 'posts/delete_tag.html'
#     url = 'tags_list_url'
#     raise_exception = True


# class Repost:
#     def get(self, request):
#         try:
#             chats = Connection2Chat.objects.filter(user=request.user)
#             return JsonResponse({'chats': chats}, status=200)
#         except Connection2Chat.DoesNotExist:
#             friends = Relations.objects.filter(user_one__user=request.user, is_friends=1)
#             return JsonResponse({'chats': []}, status=200)
#
#     def post(self, request):
#         is_2chat = False
#         response = None
#         if is_2chat:
#             pass
#         else:
#             pass
#
#     def formRepost2Wall(self):
#         pass
#     def formRepost2Chat(self):
#         pass
