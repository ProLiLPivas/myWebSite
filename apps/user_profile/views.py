from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from apps.posts.models import Post
from apps.relations.models import Relations
from .models import Profile


class UserProfile(View):
    model = Profile
    template = 'user_profile/get_user.html'

    def get(self, request, slug):

        profile = get_object_or_404(self.model, slug__iexact=slug)
        if request.user == profile.user:
            return render(request, self.template, context={
                self.model.__name__.lower(): profile,
                'posts': Post.objects.filter(user=profile.user_id),
                'user': request.user,})
        else:
            try:
                user1 = Profile.objects.get(user=request.user)
                user2 = Profile.objects.get(user=profile.user_id)
                print(type(profile))

                relations = Relations.objects.get(user_one=user1, user_two=user2)
                relations2 = Relations.objects.get(user_one=user2, user_two=user1)

                return render(request, self.template, context={
                    self.model.__name__.lower(): profile ,
                    'posts': Post.objects.filter(user=profile.user_id),
                    'user': request.user,
                    'relations': relations,
                    'relations2': relations2
                })
            except Relations.DoesNotExist:

                user1 = Profile.objects.get(user=request.user)
                user2 = Profile.objects.get(user=profile.user_id)
                relation = Relations(user_one=user1, user_two=user2)
                relation2 = Relations(user_one=user2, user_two=user1)

                r = relation.save()
                r2 = relation2.save()
                user1.save()
                user2.save()

                return render(request, self.template, context={
                    self.model.__name__.lower(): profile,
                    'posts': Post.objects.filter(user=profile.user_id),
                    'user': request.user,
                    'relations': r,
                    'relations2': r2
                })



class MyProfile(View):
    model = Profile
    template = 'user_profile/get_user.html'

    def get(self, request):
        slug = Profile.objects.get(user=request.user).slug
        return redirect('/user/' + slug)


class UpdateProfile(View):
    model = Profile
    template = 'user_profile/update_user.html'

    def get(self, request):
        profile = Profile.objects.get(user=request.user)

        return render(request, self.template, context={
            self.model.__name__.lower(): profile,
            'posts': Post.objects.filter(user=profile.user_id),
            'user': request.user,
        })



model = Profile


def subscribe(request, slug):
    profile = get_object_or_404(model, slug__iexact=slug)
    user1 = Profile.objects.get(user=request.user)
    user2 = Profile.objects.get(user=profile.user_id)

    relation_1 = Relations.objects.get(user_one=user1, user_two=user2)
    relation_1.is_subscribed = True

    user1.subscriptions += 1
    user2.subscribers += 1

    relation_1.save()
    user1.save()
    user2.save()

    return redirect('/user/' + slug)


def unsubscribe(request, slug):

            profile = get_object_or_404(model, slug__iexact=slug)
            user1 = Profile.objects.get(user=request.user)
            user2 = Profile.objects.get(user=profile.user_id)

            relation_1 = Relations.objects.get(user_one=user1, user_two=user2)
            relation_1.is_subscribed = False
            user1.subscriptions -=1
            user2.subscribers -= 1

            relation_1.save()
            user1.save()
            user2.save()

            return redirect('/user/' + slug)


def add2friends(request, slug):

            profile = get_object_or_404(model, slug__iexact=slug)
            user1 = Profile.objects.get(user=request.user)
            user2 = Profile.objects.get(user=profile.user_id)

            relation_1 = Relations.objects.get(user_one=user1, user_two=user2)
            relation_2 = Relations.objects.get(user_one=user2, user_two=user1)

            relation_1.is_subscribed = True
            relation_1.is_friends, relation_2.is_friends = True, True
            user1.subscriptions += 1
            user1.friends += 1
            user2.subscribers += 1
            user2.friends += 1

            user1.save()
            user2.save()
            relation_1.save()
            relation_2.save()

            return redirect('/user/' + slug)


def remove(request, slug):

    profile = get_object_or_404(model, slug__iexact=slug)
    user1 = Profile.objects.get(user=request.user)
    user2 = Profile.objects.get(user=profile.user_id)

    relation_1 = Relations.objects.get(user_one=user1, user_two=user2)
    relation_2 = Relations.objects.get(user_one=user2, user_two=user1)

    relation_1.is_subscribed = False
    relation_1.is_friends, relation_2.is_friends = False, False
    user1.subscriptions -= 1
    user1.friends -= 1
    user2.subscribers -= 1
    user2.friends -= 1

    user1.save()
    user2.save()
    relation_1.save()
    relation_2.save()
    return redirect('/user/' + slug)



#
# class Friends(View):
#
#     template = 'relations/friends.html'
#
#     def get(self, request):
#         friends = Relations.objects.filter(user_one__user=request.user, is_friends=1)
#         return render(request, self.template, context={'friends': friends, })
#
#
# class Subs(View):
#
#     template = 'relations/subs.html'
#
#     def get(self, request):
#         subs = Relations.objects.filter(user_one__user=request.user, is_subscribed=1)
#         return render(request, self.template, context={'subs': subs})
#
#
# class Search(View):
#
#     template = 'relations/search.html'
#
#     def get(self, request):
#         users = Profile.objects.all
#         return render(request, self.template, context={'users': users})
