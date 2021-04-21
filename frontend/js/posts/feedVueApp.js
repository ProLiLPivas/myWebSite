import {createFeed, startCreatingPost, createPost, showUpdatePost, updatePost, delPost, getPostUrl } from './postScripts.js';
import { getTagUrl, attachTag, unattachTag } from './tagScripts.js'
import { likePost, likeComment } from './likeScripts.js' ;
import { getComment, postComment, delComment,  showUpdateComment, updateComment, answerComment } from './commentScripts.js';
import { showSettings, setSettings, changeSettings }  from './postSettingsScripts.js';
import {getChats, addChat2Repost, repostToChat, repostToWall} from './repostScripts.js';
import {UrlsList} from "./urls.js";


var app = new Vue({
    el: '#feed',
    data: {
        show_create: false,
        newPost: [],
        feed: [],
        user: {},
    },
    created() {
        createFeed(this);
    },

    methods: {
        getPostUrl: function(post){ getPostUrl(post) },
        startCreatingPost: function() { startCreatingPost(this) },
        createPost: function(post) { createPost(post, this) },
        showUpdatePost: function(post) { showUpdatePost(post) },
        updatePost: function(post) { updatePost(post) },
        delPost: function(post_number, id) { delPost(post_number, id, this) },

        getTagUrl: function (tag) { getTagUrl(tag); },
        attachTag: function(post){ attachTag(post) },
        unattachTag: function(post, index) { unattachTag(post, index) },

        getComment: function(post) { getComment(post) },
        postComment: function(post) { postComment(post) },
        delComment: function(post, comment_number) { delComment(post, comment_number) },
        showUpdateComment: function(post, comment_number) { showUpdateComment(post, comment_number) },
        updateComment: function (post, comment_number) { updateComment(post, comment_number) },

        likeComment: function(post, comment_number) { likeComment(post, comment_number) },
        makeLike: function(post) { likePost(post) },

        showSettings: function (post) { showSettings(post) },
        changeSettings: function (post) { changeSettings(post) },

        //fromSettingsData: function(dataInstance, post){},
        setSettings: function(post){ setSettings(post)},

        getChats: function (post) {},
        addChat2Repost: function(post, chat_id){},
        repostToChat: function () {},
        repostToWall: function (post) {},

        get_feed: function(){ return this.feed },
    },
});

export {app}