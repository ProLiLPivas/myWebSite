from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from apps.user_profile.utils.profile_utils import *


class RelatedUsersView:
    """ """
    key = ''
    slug_query_parameter: str = ''
    second_condition: tuple = ('id', 1)
    post_action_func = lambda *args: print('u dont using any func')
    is_have_post_method: bool = True
    template = 'profile/friends.html'

    def get(self, request, slug=None):
        if slug and not request.is_ajax():
            return HttpResponse(status=404)
        elif not slug:
            if not request.is_ajax():
                return render(request, self.template)
            else:
                slug = request.user.profile.slug
        query = ((self.slug_query_parameter, slug), self.second_condition)
        rel = get_relations_list(query)

        for user in rel:  # !!! remove later !!!
            user['avatar'] = ''
            user['url'] = '/user/' + user['slug'] + '/'
            user['chat_url'] = '/messages/id=' + str(user['id']) + '/'
        return JsonResponse({'related_users': rel, 'key': self.key}, status=200)

    def post(self, request, slug):
        if self.is_have_post_method:
            change_relations_status(self.post_action_func, slug, request.user.profile)
            return redirect('/user/' + slug)
        return HttpResponse(status=405)
