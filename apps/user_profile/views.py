from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from apps.posts.models import Post
from .models import Profile, UsersRelation


class UserProfile(View):
    model = Profile
    template = 'user_profile/get_user.html'

    def get_relations_status(self, relation: UsersRelation):

        if relation.is_friends:
            return 3
        elif relation.is_subscribed:
            return 2
        elif relation.is_block: # if u blocked u cant see of do any anything with profile, cant messaging, cant add 2 friend
            return 0
        else:
            return 1


    def get(self, request, slug):

        profile = get_object_or_404(self.model, slug__iexact=slug)
        if request.user == profile.user:
            return render(request, self.template, context={
                'profile': profile,
                'posts': Post.objects.filter(user=profile.user_id),
                'user': request.user,
                'status': 5
            })
        else:
            try:
                user1 = Profile.objects.get(user=request.user)
                user2 = Profile.objects.get(user=profile.user_id)

                relations = UsersRelation.objects.get(main_user=user1, secondary_user=user2)
                relations2 = UsersRelation.objects.get(main_user=user2, secondary_user=user1)

                return render(request, self.template, context={
                    self.model.__name__.lower(): profile ,
                    'posts': Post.objects.filter(user=profile.user_id),
                    'user': request.user,
                    'relations': relations,
                    'relations2': relations2,
                    'status': self.get_relations_status(relations)
                })
            except UsersRelation.DoesNotExist:
                user1 = Profile.objects.get(user=request.user)
                user2 = Profile.objects.get(user=profile.user_id)
                relation = UsersRelation(main_user=user1, secondary_user=user2)
                relation2 = UsersRelation(main_user=user2, secondary_user=user1)

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

    relation_1 = UsersRelation.objects.get(main_user=user1, secondary_user=user2)
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

            relation_1 = UsersRelation.objects.get(main_user=user1, secondary_user=user2)
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

            relation_1 = UsersRelation.objects.get(main_user=user1, secondary_user=user2)
            relation_2 = UsersRelation.objects.get(main_user=user2, secondary_user=user1)

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

    relation_1 = UsersRelation.objects.get(main_user=user1, secondary_user=user2)
    relation_2 = UsersRelation.objects.get(main_user=user2, secondary_user=user1)

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




class Friends(View):

    template = 'user_profile/friends.html'

    def get(self, request):
        friends = UsersRelation.objects.filter(main_user__user=request.user, is_friends=1)
        return render(request, self.template, context={'friends': friends, })


class Subs(View):

    template = 'user_profile/subs.html'

    def get(self, request):
        subs = UsersRelation.objects.filter(main_user__user=request.user, is_subscribed=1)
        return render(request, self.template, context={'subs': subs})


class Search(View):

    template = 'user_profile/search.html'

    def get(self, request):
        users = Profile.objects.all
        return render(request, self.template, context={'users': users})
