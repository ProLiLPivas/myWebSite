import {created, getTagUrl} from "./feedScripts";


new Vue({
    el: '#start_page',
    data: {
        show_create: false,
        newPost: [],
        feed: [],
        user: {},
    },
    created() {
        created('/blog')
    },
    methods: {
        getTagUrl: function (tag) { getTagUrl(tag); },
        unattachTag: function() { unattachTag() },
        startCreatingPost: function() { startCreatingPost() },
        showUpdatePost: function(post) { showUpdatePost(post) },
        create_or_updatePost: function(post, is_update = false) { create_or_updatePost(post, is_update = false) },
        delPost: function(post_number, id) { delPost(post_number, id) },
        makeLike: function(post) { makeLike(post) },
        getComment: function(post) { getComment(post) },
        postComment: function(post) { postComment(post) },
        likeComment: function(post, comment_number) { likeComment(post, comment_number) },
        delComment: function(post, comment_number) { delComment(post, comment_number) },
        showUpdateComment: function(post, comment_number) { showUpdateComment(post, comment_number) },
        updateComment: function (post, comment_number) { updateComment(post, comment_number) },
        showSettings: function (post) { showSettings(post) },
        changeSettings: function (post) { changeSettings(post) },
    },
});

