from django.shortcuts import render
from django.views import View

from apps.relations.models import Relations
from apps.user_profile.models import Profile


class Friends(View):

    template = 'relations/friends.html'

    def get(self, request):
        friends = Relations.objects.filter(user_one__user=request.user, is_friends=1)
        return render(request, self.template, context={'friends': friends, })


class Subs(View):

    template = 'relations/subs.html'

    def get(self, request):
        subs = Relations.objects.filter(user_one__user=request.user, is_subscribed=1)
        return render(request, self.template, context={'subs': subs})


class Search(View):

    template = 'relations/search.html'

    def get(self, request):
        users = Profile.objects.all
        return render(request, self.template, context={'users': users})









# class Friends(View):
#
#     template = 'relations/friends.html'
#
#     def get(self, request):
#
#         friends = Relations.objects.filter(user_one=request.user, is_friends=1)
#
#         # friends += Relations.objects.get(user_one=user, is_friends=1)
#
#         return render(request, self.template, context={'friends': friends, })
#
#
#
#
#
# class Subs(View):
#
#     template = 'relations/subs.html'
#
#     def get(self, request):
#         subs = Relations.objects.filter(user_one=request.user , is_subscribed=1)
#         return render(request, self.template, context={'subs': subs})
#
#
# class Search(View):
#     template = 'relations/search.html'
#
#     def get(self, request):
#         users = User.objects.all
#         return render(request, self.template, context={'users': users})
