import {makeAjaxRequest} from "../ajaxScripts.js";
import {Post} from "./Post.js";


function getChats(post) {
    makeAjaxRequest('get', '')
        .then(response => {
            post.chats4repost = response.data.chats;
        });
}

function addChat2Repost(post, chat_id){
    var index = post.selected2repost.indexOf(chat_id);
    if(index === -1){
        post.selected2repost.push(chat_id)
    }else {
        delete post.selected2repost.splice(index, 1)
    }
}

function repostToChat() {}

function repostToWall(post) {
    var repost = new Post();
    repost.postTitle = post.title;
    repost.postBody = post.repostInput
}

export {getChats, addChat2Repost, repostToChat, repostToWall}