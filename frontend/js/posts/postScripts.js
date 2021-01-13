import {makeAjaxRequest} from "../ajaxScripts.js";
import {fromSettingsData, changeSettings} from "./postSettingsScripts.js"
import {UrlsList} from "./urls.js";
import {Post} from "./Post.js";

function getPostUrl(post){
    return '/feed/post=' + post.id + '/'
}


function createFeed(vue_obj){
    makeAjaxRequest('get', UrlsList.urlsList.getFeedUrl)
        .then(response =>{
            vue_obj.feed = response.data.posts.map(function(post){
                return  new Post(post);
            });
            vue_obj.user = response.data.user;
        })
}

function startCreatingPost(vue_obj){
    vue_obj.show_create = !vue_obj.show_create;
    if(vue_obj.show_create){
        vue_obj.newPost = [new Post()];
        vue_obj.newPost[0].data.see_comments_permission = 1;
        vue_obj.newPost[0].data.comment_permission = 1;
        vue_obj.newPost[0].data.like_permission = 1;
        vue_obj.newPost[0].data.repost_permission = 1;
        vue_obj.newPost[0].data.see_statistic_permission = 1;
        vue_obj.newPost[0].data.see_author_permission = 1;
        vue_obj.newPost[0].data.see_post_permission = 1;
    }else {
        vue_obj.newPost = null
    }
}

function createPost(post, vue_obj) {
    var formData = new FormData();
    formData.append('title', post.postTitle);
    formData.append('body', post.postBody);
    formData.append('tags', post.attachedTags);
    formData.append('post_id', post.id);
    formData = fromSettingsData(formData, post);
    console.log(211);
    makeAjaxRequest('post',  UrlsList.urlsList.cretePostUrl, formData)
        .then(response => {
            vue_obj.show_create = false;
            var new_post = new Post(response.data.post);
            new_post.id = new_post.data.id;
            new_post.data.url = '/user/me';
            new_post.data.username = vue_obj.user.username;
            new_post.tags = new_post.data.tag;
            new_post.settings = post.settings;
            if (new_post.settings.length !== 0) {
                changeSettings(new_post);
            }
            vue_obj.feed.unshift(new_post);
            console.log(vue_obj.feed)
        });
}

function showUpdatePost(post){
    post.show_upd = !post.show_upd;
    if(post.show_upd){
        post.show_settings = false;
        post.postTitle = post.data.title;
        post.postBody = post.data.body;
        post.attachedTags = post.tags.map(tag =>{ return tag.title});
    }
}


function updatePost(post){
    var formData = new FormData();
    formData.append('title', post.postTitle);
    formData.append('body', post.postBody);
    formData.append('tags', post.attachedTags);
    formData.append('post_id', post.id);

    makeAjaxRequest('post', UrlsList.urlsList.updatePostUrl, formData)
        .then(response =>{
            post.show_upd = false;
            post.data.title = post.postTitle;
            post.data.body = post.postBody;
            post.tags = response.data.tag;
            post.data.is_changed = true;
        });
}

function delPost(post_number, id, vue_obj){
    var formData = new FormData();
    formData.append('id', id);
    makeAjaxRequest('post', UrlsList.urlsList.deletePostUrl, formData)
        .then(response =>{
            vue_obj.show_del = false;
            delete vue_obj.feed.splice(post_number, 1);
        });
}

// TAGS

export { createFeed, startCreatingPost, createPost, showUpdatePost, updatePost, delPost, getPostUrl}