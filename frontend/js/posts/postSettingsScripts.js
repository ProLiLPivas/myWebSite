import {makeAjaxRequest} from "../ajaxScripts.js";
import {UrlsList} from "./urls.js";


function showSettings(post){
    post.show_settings = !post.show_settings;
    if(post.settings){
        post.settings = {
            'see_comments_permission': post.data.see_comments_permission,
            'comment_permission': post.data.comment_permission,
            'like_permission': post.data.like_permission,
            'repost_permission': post.data.repost_permission,
            'see_statistic_permission': post.data.see_statistic_permission,
            'see_author_permission': post.data.see_author_permission,
            'see_post_permission': post.data.see_post_permission,
        }
    }
}

function changeSettings(post){
    let formData = new FormData();
    formData = fromSettingsData(formData, post);
    makeAjaxRequest('post', UrlsList.urlsList.postSettingsUrl, formData)
        .then(response =>{
            post.show_upd = false;
            setSettings(post)
        })
}

function fromSettingsData(dataInstance, post){
    dataInstance.append('post_id', post.id);
    dataInstance.append('see_comments_permission', post.settings.see_comments_permission);
    dataInstance.append('comment_permission', post.settings.comment_permission);
    dataInstance.append('like_permission', post.settings.like_permission);
    dataInstance.append('repost_permission', post.settings.repost_permission);
    dataInstance.append('see_statistic_permission', post.settings.see_statistic_permission);
    dataInstance.append('see_author_permission', post.settings.see_author_permission);
    dataInstance.append('see_post_permission', post.settings.see_post_permission);
    return dataInstance;
}

function setSettings(post){
    post.show_settings = false;
    post.data.see_comments_permission = post.settings.see_comments_permission;
    post.data.comment_permission =  post.settings.comment_permission;
    post.data.like_permission = post.settings.like_permission;
    post.data.repost_permission = post.settings.repost_permission;
    post.data.see_statistic_permission = post.settings.see_statistic_permission;
    post.data.see_author_permission = post.settings.see_author_permission;
    post.data.see_post_permission = post.settings.see_post_permission;
}

export {showSettings, fromSettingsData, setSettings, changeSettings}