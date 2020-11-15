from django.forms import model_to_dict

from apps.posts.forms import *
from apps.posts.models import *
from apps.relations.models import Relations
from apps.user_profile.models import Profile


class PostUtils:

    @staticmethod
    def create_post(data, user):
        bound_form = PostForm(data)
        if bound_form.is_valid():

            new_post = bound_form.save(commit=False)
            new_post.user = user
            profile = user.profile
            profile.posts += 1
            profile.save()
            new_post.save()

            return new_post

    @staticmethod
    def create_or_get_tags(t, new_obj):
        tags = PostSerializer.parseTags(t)
        tags_dict = []
        if tags != ['']:
            for tag in tags:
                new_tag = Tag.objects.get_or_create(title=tag.__str__())
                new_obj.tag.add(new_tag[0])
                tags_dict.append(model_to_dict(new_tag[0]))
        return tags_dict

    @staticmethod
    def update_post(data, post_id, user):
        post = Post.objects.get(id=post_id)
        if post.user == user:
            bound_form = PostForm(data, instance=post)

            if bound_form.is_valid():
                new_obj = bound_form.save()
                new_obj.is_changed = True
                new_obj.save()
                return  new_obj, 200
        return None, 403

    @staticmethod
    def del_post(id , user):
        obj = Post.objects.get(id=int(id))
        if user == obj.user or user.is_staff:
                user_object = Profile.objects.get(id=user.id)
                user_object.posts -= 1
                user_object.save()
                obj.delete()
                return {'posts_amount': user_object.posts}
        else:
            return None

    @staticmethod
    def create_comment(bound_form, user, id):
        post = Post.objects.get(id=id)
        if  post.comment_permission <= PostUtils.get_permission(post, user):
            if bound_form.is_valid():
                new_comment = bound_form.save(commit=False)
                if new_comment.text != 'null':
                    post.comments_amount += 1
                    new_comment.post = post
                    new_comment.user = user
                    new_comment.save()
                    post.save()
                    return PostSerializer.new_comment_to_dict(new_comment, post.comments_amount,  user), 200
            return None, 403
        return None, 403

    @staticmethod
    def update_comment(comment_id, text, user):
        com_obj = Comment.objects.get(id=comment_id)
        if com_obj.user == user:
            bound_form = CommentForm({'text': text}, instance=com_obj)
            if bound_form.is_valid():
                comment = bound_form.save(commit=False)
                comment.is_changed = True
                comment.save()
                return text, 200

    @staticmethod
    def del_comment(id, post_id, user):
        obj = Comment.objects.get(id=int(id))
        post_object = Post.objects.get(id=int(post_id))
        if user == obj.user or user == post_object.user or user.is_staff:
            post_object.comments_amount -= 1
            post_object.save()
            obj.delete()
            return {'comment_amount': post_object.comments_amount}
        else: return None

    @staticmethod
    def like_object(like, model_obj):
        if like != 0 and model_obj != 0:
            if not like.exist:
                like.exist = True
                model_obj.likes_amount += 1
            else:
                like.exist = False
                model_obj.likes_amount -= 1
            like.save()
            model_obj.save()
            return {'is_liked': like.exist, 'amount': model_obj.likes_amount}
        else: return []

    @staticmethod
    def chose_instance(id, user, model):
        model_obj = model.objects.get(id=int(id))
        if model == Post:
            if model_obj.like_permission <= PostUtils.get_permission(model_obj, user):
                return (Like.objects.get_or_create(user=user, post=model_obj))[0], model_obj
            else: return 0, 0
        elif model == Comment:
            return (Like.objects.get_or_create(user=user, comment=model_obj))[0], model_obj
        else:
            return None, None

    @staticmethod
    def repost(post, user):
        if post.repost_permission <= PostUtils.get_permission(post, user):
            pass


    @staticmethod
    def get_permission(post, user):
        if post.user == user:
            return 4
        rel = Relations.objects.get_or_create(user_one=post.user.profile, user_two=user.profile)
        rel = rel[0]
        if rel.is_friends:
            return 3
        elif rel.is_subscribed:
            return 2
        elif rel.is_block:
            return 0
        else:
            return 1

    @staticmethod
    def set_post_permissions(data, user):
        post = Post.objects.get(id=int(data['post_id']))
        if post.user == user:
            bound_form = PostSettingsForm(data, instance=post)
            if bound_form.is_valid() and post.user == user:
                bound_form.save()
                return 200
        return 403

class PostSerializer:

    @staticmethod
    def feed_to_dict(posts, user):    # BECOME SERIALIZER IN FUTURE
        feed_dict = []
        for post in posts:
            permission = PostUtils.get_permission(post, user,)
            if post.see_post_permission <= permission:
                post_dict = model_to_dict(post)
                if post.see_author_permission <= permission:
                    post_dict['username'] = post.user.username
                    post_dict['url'] = post.user.profile.get_absolute_url()
                    post_dict['permission'] = permission
                else:
                    post_dict['user'] = 0
                    post_dict['username'] = 'Anonymous'
                    post_dict['url'] = ''

                if post.see_statistic_permission <= permission:
                    if post.like_permission <= permission:
                        like = Like.objects.filter(post=post_dict['id'])
                        if like:
                            if like[0].exist:
                                post_dict['is_liked'] = True
                        else:
                            post_dict['is_liked'] = False
                    # if post.like_permission <= permission:
                    #     post_dict['is_liked'] = False
                    #     post_dict['likes_amount'] = 0
                    # if post.comment_permission <= permission:
                    #     post_dict['comments_amount'] = 0
                    # if post.repost_permission <= permission:
                    #     post_dict['reposts_amount'] = 0
                else:
                    post_dict['is_liked'] = False
                    post_dict['likes_amount'] = 0
                    post_dict['comments_amount'] = 0
                    post_dict['reposts_amount'] = 0

                if post_dict['tag']:
                        tags = []
                        for tag in post_dict['tag']:
                            m2d = model_to_dict(tag)
                            tags.append(m2d)
                        post_dict['tag'] = tags
                feed_dict.append(post_dict)
        return feed_dict

    @staticmethod
    def new_comment_to_dict(comment, amount, user):
        comment = model_to_dict(comment)
        comment['comments_amount'] = amount
        comment['user_id'] = user.id
        comment['username'] = user.username
        comment['url'] = user.profile.get_absolute_url()
        return comment

    @staticmethod
    def comments_to_dict(id, user):   # BECOME SERIALIZER IN FUTURE
        post = Post.objects.get(id=id)
        if post.see_comments_permission <= PostUtils.get_permission(post, user):
            comments = list(Comment.objects.filter(post=post).values())
            if comments:
                for comment in comments:
                    user = User.objects.get(id=comment['user_id'])
                    comment['username'] = user.username
                    comment['url'] = user.profile.get_absolute_url()
                    like = Like.objects.filter(comment=comment['id'])
                    if like:
                        if like[0].exist:
                            comment['is_liked'] = True
                    else:
                        comment['is_liked'] = False
        else: comments = []
        return comments

    @staticmethod
    def parseTags(tags_text):
        tag = ''
        tags = []
        for symbol in tags_text:
            if not symbol == ',':
                tag += symbol
            else:
                tags.append(tag)
                tag = ''
        tags.append(tag)
        return tags
