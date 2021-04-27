from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import model_to_dict
from django.views.generic import View

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from .serializers import *

from apps.posts.utils.post_mixins import *
from apps.message.views import APIChatsList
from .forms import *
from .models import *


def like_object(obj):
    if obj[1]:
        return
    obj[0].is_exist = not obj[0].is_exist
    obj[0].save()
    return


class APIPostsList(APIView):
    def get(self, request,):
        queryset = Post.objects.filter()
        serializer = FeedSerializer(
                queryset, many=True, context={'request': request})
        return Response(serializer.data)


class APIPost(APIView):
    def get(self, request, id):
        queryset = Post.objects.filter(id=id)
        serializer = SinglePostSerializer(
                queryset, many=True, context={'request': request})
        return Response(serializer.data)


class APICreatePost(APIView):

    def post(self, request):

        context = {
            'tags': request.data.get('tags', '').split(','),
            'user': {'user': request.user},
            'permission_settings': request.data.get('permission_settings', {})
        }

        serializer = CreatePostSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(status=201)
        print(serializer.errors)
        return Response()




class APIEditPost(APIView):

    def put(self, request, id):
        post = Post.objects.get(id=id)
        if request.user == post.user:
            context = {
                'tags': request.data.get('tags', '').split(','),
                'permission_settings': request.data.get('permission_settings', {})
            }
            serializer = UpdateSerializer(
                instance=post, data=request.data, context=context)
            print(serializer)
            if serializer.is_valid():
                serializer.save(is_changed=True)
                return Response(status=201)
            return Response(status=400)
        return Response(status=403)


    def patch(self, request, id):
        post = Post.objects.get(id=id)
        if post.like_permission < post.get_relations_status(request.user):
            like_object(PostLike.objects.get_or_create(user=request.user, obj=post))
            return Response(status=201)
        return Response(status=403)

    def delete(self, request, id):
        post = Post.objects.get(id=id)
        if request.user == post.user or request.user.is_staff:
            post.delete()
            return Response(status=204)
        return Response(status=403)


class APIComments(APIView):

    def get(self, request, id):
        post = Post.objects.get(id=id)
        if post.see_comments_permission <= post.get_relations_status(
                request.user):
            queryset = Comment.objects.filter(post=post)
            serializer = CommentsSerializer(queryset, many=True, context={'request': request})
            return Response(serializer.data)
        return Response(status=403)

    def post(self, request, id):
        post = Post.objects.get(id=id)
        if post.comment_permission <= post.get_relations_status(request.user):
            if request.data.get('text'):
                context = {'user': request.user, 'post': post}
                serializer = CreateCommentSerializer(data=request.data, context=context)
                if serializer.is_valid():
                    serializer.save()
                    return Response(status=201)
            return Response(status=400)
        return Response(status=403)


class APIEditComment(APIView):

    def put(self, request, id):
        comment = Comment.objects.get(id=id)
        if request.user == comment.user:
            if request.data.get('text'):
                serializer = CreateCommentSerializer(data=request.data, instance=comment)
                if serializer.is_valid():
                    serializer.save(is_changed=True)
                    return Response(status=201)
            return Response(status=400)
        return Response(status=403)

    def patch(self, request, id):
        comment = Comment.objects.get(id=id)
        if comment.post.see_comments_permission <= \
                comment.post.get_relations_status(request.user):
            like_object(CommentLike.objects.get_or_create(
                    user=request.user, obj=comment))
            return Response(status=201)
        return Response(status=403)

    def delete(self, request, id):
        comment = Comment.objects.get(id=id)
        if request.user == comment.user or request.user == comment.post.user \
                or request.user.is_staff:
            comment.delete()
            return Response(status=204)
        return Response(status=403)


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


class APIRepost(APIChatsList):
    pass


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
    model_form = None

    def post(self, request):
        new_post = PostUtils.create_post(request.POST, request.user)
        tags = PostUtils.create_or_get_tags(request.POST['tags'], new_post)
        post_dict = model_to_dict(new_post)
        post_dict['tag'] = tags
        return JsonResponse({'post': post_dict}, status=200)


class UpdatePost(View, LoginRequiredMixin):
    model = Post
    model_form = None

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
