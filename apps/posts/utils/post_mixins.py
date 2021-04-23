from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from apps.posts.models import Post
from apps.posts.utils.post_utils import PostUtils, PostSerializer
from apps.posts.serializers import FeedSerializer

class FeedMixin:
    template = None
    query_parameters = Q()
    ordering = ('-date_publication',)

    def get(self, request, slug=''):  # feed # only friends # popular   # all

        if request.is_ajax():
            if slug and not self.query_parameters[1]:
                query = Q((self.query_parameters[0], slug))
            else:
                query = Q(self.query_parameters)
            posts = Post.objects.filter(query).order_by(*self.ordering)
            feed_dict = PostSerializer.feed_to_dict(posts, request.user)
            users_dict = {'id': request.user.id, 'username': request.user.username,  'is_staff': request.user.is_staff}
            print(JsonResponse({'posts': feed_dict, 'user': users_dict, 'url': request.path}, status=200))
            return JsonResponse({'posts': feed_dict, 'user': users_dict, 'url': request.path}, status=200)
        return render(request, self.template, context={'url': request.path, 'slug': slug})


class LikeMixin:
    model = None

    def post(self, request):
        like, model_obj = PostUtils.chose_instance(request.POST['object_id'], request.user, self.model)
        response = PostUtils.like_object(like, model_obj)
        if response:
            return JsonResponse(response, status=200)
        else:
            return HttpResponse(status=403)