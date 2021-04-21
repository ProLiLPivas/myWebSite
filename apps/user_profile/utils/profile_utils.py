from django.db.models import Q
from django.forms import model_to_dict

from apps.user_profile.models import Profile, UsersRelation


def get_profile_and_relations(slug, your_profile):
    profile = Profile.objects.get(slug__iexact=slug)
    relation = UsersRelation.objects.get_or_create(
        main_user_profile=your_profile, secondary_user_profile=profile)[0]
    return profile, relation


def get_profile_context(slug, users_profile, path):
    profile, relation_with_you = get_profile_and_relations(slug, users_profile)
    status = relation_with_you.get_relations_status()

    if status == -1:
        return {'profile': {'user': profile.user, }, 'status': status}

    profile_dict = model_to_dict(profile)
    profile_dict['username'] = profile.user.username
    return {
        'profile': profile_dict,
        'relations': relation_to_dict(relation_with_you),
        'status': status,
        'slug': slug,
        'url': path,
    }


def get_relations_list(query):
    users_relation_queryset = list(UsersRelation.objects.filter(Q(*query)))
    return [model_to_dict(user.secondary_user_profile) for user in
            users_relation_queryset]


def relation_to_dict(relation):
    if relation:
        print(relation.is_friends , relation.is_subscribed ,
              relation.is_blocked)
        return {
            'is_friends': int(relation.is_friends) ,
            'is_subscribed': int(relation.is_subscribed) ,
            'is_block': int(relation.is_blocked)
        }
    return []


def subscribe_or_unsubscribe(_, relation_obj):
    # _ must be here without it dont work
    sub_changes = (+1 , -1)[relation_obj.is_subscribed]

    relation_obj.is_subscribed = not relation_obj.is_subscribed
    relation_obj.main_user_profile.subscriptions += sub_changes
    relation_obj.secondary_user_profile.subscribers += sub_changes

    relation_obj.main_user_profile.save()
    relation_obj.secondary_user_profile.save()
    relation_obj.save()


def add_or_remove_friends(_, relation_obj):
    # _ must be here without it dont work
    subscribe_or_unsubscribe(_ , relation_obj)
    sub_changes = (+1 , -1)[relation_obj.is_friends]

    relation_obj.is_friends = not relation_obj.is_friends
    relation_obj.related_object.is_friends = not relation_obj.related_object.is_friends
    relation_obj.main_user_profile.friends += sub_changes
    relation_obj.secondary_user_profile.friends += sub_changes

    relation_obj.main_user_profile.save()
    relation_obj.secondary_user_profile.save()
    relation_obj.save()
    relation_obj.related_object.save()


def block_unblock_user(_, relation_obj):
    # _ must be here without it dont work
    relation_obj.related_object.is_blocked = not relation_obj.is_blocked
    relation_obj.save()


def change_relations_status(func_obj, slug, users_profile):
    relation_with_you = UsersRelation.objects.get(
        main_user_profile=users_profile, secondary_user_profile__slug=slug)
    func_obj(relation_with_you)
