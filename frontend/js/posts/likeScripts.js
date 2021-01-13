import {makeAjaxRequest} from "../ajaxScripts.js";
import {UrlsList} from "./urls.js";


function likePost(post) {
    var formData = new FormData();
    formData.append('object_id', post.id);
    var ajax = makeAjaxRequest('post', UrlsList.urlsList.likePostUrl, formData);
    ajax.then(response => {
        post.data.is_liked = response.data.is_liked;
        post.data.likes_amount = response.data.amount
    });
}

function likeComment(post, comment_number){
    var formData = new FormData();
    formData.append('object_id', post.comments[comment_number].id);
    var ajax = makeAjaxRequest('post', UrlsList.urlsList.likeCommentUrl, formData);
    ajax.then( response =>{
        post.comments[comment_number].likes_amount = response.data.amount;
        post.comments[comment_number].is_liked = response.data.is_liked;
    });
}

export {likePost, likeComment}