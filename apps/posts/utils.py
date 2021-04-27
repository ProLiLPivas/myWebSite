from django.db.models import Q

from apps.posts.models import BaseLike, Post


def like_object(obj: (BaseLike, bool)):
    if obj[1]:
        return
    obj[0].is_exist = not obj[0].is_exist
    obj[0].save()
    return

def update_tags(instance: Post, tags: str):
        query = Q()
        for tag in tags:
            query = query | Q(title=tag)
        instance.tag.remove(*list(instance.tag.exclude(query)))
        existing_tags = list(instance.tag.all().values('title'))
        for tag in tags:
            if not {'title': tag} in existing_tags:
                instance.tag.get_or_create(title=tag)



a = {"text": "1111"}

b = {
    "permission_settings": {
        "see_comments_permission": 3,
        "comment_permission": 2,
        "like_permission": 1,
        "repost_permission": 0,
        "see_statistic_permission": 0,
        "see_author_permission": 0,
        "see_post_permission": 1
    },
    "tags": "0,1336",
    "title": "111",
    "body": "_ . _ . _"
}