import {makeAjaxRequest} from "../ajaxScripts.js";
import {UrlsList} from "./urls.js";

function getComment(post) {
    //post = this.feed[post_number];
    post.show_comments = !post.show_comments;
    if(post.show_comments){
        var url = UrlsList.urlsList.commentUrl.replace('{post_id}', post.id);
        var a = makeAjaxRequest('get', url);
        a.then(response => {
            post.comments = response.data.comments;
        })
    }
}

function postComment(post) {
    var formData = new FormData();
    //post = this.feed[post_number];
    if(post.commentInput === null || post.commentInput === '') {return}
    formData.append('post', post.id);
    formData.append('text', post.commentInput);
    var url = UrlsList.urlsList.commentUrl.replace('{post_id}', post.id);
    var ajax = makeAjaxRequest('post', url, formData);
    ajax.then(response => {
        if (post.comments){
            post.comments.unshift(response.data.comment);
        }else{
            post.comments = [response.data.comment];
        }
        post.commentInput = '';
        post.data.comments_amount = response.data.comment.comments_amount ;
    });
}

function delComment(post, comment_number){
    var formData = new FormData();
    formData.append('id', post.comments[comment_number].id);
    formData.append('post_id', post.id);

    var ajax = makeAjaxRequest('post', UrlsList.urlsList.deleteCommentUrl, formData);
    ajax.then(response => {
        delete post.comments.splice(comment_number, 1);
        post.data.comments_amount = response.data.comment_amount;
    });
}

function showUpdateComment(post, comment_number){
    if(post.show_com_upd === comment_number){
        post.show_com_upd = '';
        post.updateInput = '';
    }else {
        post.show_com_upd = comment_number;
        post.updateInput = post.comments[comment_number].text;
    }
}

function updateComment(post, comment_number){
    var formData = new FormData();
    //post = post = this.feed[post_number];
    formData.append('comment_id', post.comments[comment_number].id);
    formData.append('new_text', post.updateInput);
    var ajax = makeAjaxRequest('post', UrlsList.urlsList.updateCommentUrl, formData);
    ajax.then(response => {
        post.comments[comment_number].text = post.updateInput;
        post.comments[comment_number].is_changed = true;
        post.show_com_upd = '';
        post.updateInput = '';
    });
}

function answerComment() { }

export { getComment, postComment, delComment,  showUpdateComment, updateComment, answerComment }