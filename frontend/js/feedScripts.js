function makeAjaxRequest(method, url, data=null){
                return axios({
                    method: method,
                    url: url,
                    data: data,
                    xsrfCookieName: 'csrftoken',
                    xsrfHeaderName: 'X-CSRFToken',
                    headers :{
                        'Access-Control-Allow-Origin': '*',
                        'X-Requested-With':'XMLHttpRequest'
                    },
                });
            }

class Post{
    constructor(data=null, is_likes=false){
        if(data){
            this.data = data;
            this.id = data['id'];
            this.tags = data['tag'];
        }
    }

    id = 0;
    data = [];
    tags = [];
    postTitle = '';
    postBody = '';

    show_comments = null;
    comments = [];
    settings = [];
    commentInput = '';
    show_com_upd = '';
    updateInput = '';
    show_upd = false;
    show_rep = false;
    show_del = false;
    show_settings = false;

    tagInput = '';
    show_tag_input = false;
    attachedTags = [];

}
export {created, getChats}

export function created(feed_url){
            makeAjaxRequest('get', feed_url)
                .then(response => {
                    this.feed = response.data.posts.map(function (post) {
                        return new Post(post);
                    });
                    this.user = response.data.user;
                });
}



export function getTagUrl(tag){
        return 'tag=' + tag + '/'
}

export function attachTag(post) {
    if(post.attachedTags.indexOf(post.tagInput) === -1){
        post.attachedTags.push(post.tagInput);
        post.tagInput = '';
    }
}

export function unattachTag (post, index) {
    delete post.attachedTags.splice(index, 1)
}

export function startCreatingPost(){
    this.show_create = !this.show_create;
    if(this.show_create){
        this.newPost = [new Post()]
    }else {
        this.newPost = null
    }
}

export function showUpdatePost(post){
    post.show_upd = !post.show_upd;
    if(post.show_upd){
        post.show_settings = false;
        post.postTitle = post.data.title;
        post.postBody = post.data.body;
        post.attachedTags = post.tags.map(tag =>{ return tag.title});
    }
}

export function create_or_updatePost(post, is_update=false) {
    var formData = new FormData();
    formData.append('title', post.postTitle);
    formData.append('body', post.postBody);
    formData.append('tags', post.attachedTags);
    formData.append('is_update', is_update);
    formData.append('post_id', post.id);
    if(is_update){url = ''}     // upd url
    else {url = ''}     // cre url
    var ajax = makeAjaxRequest('post', url , formData);
    ajax.then(response =>{
        if(is_update){
            post.show_upd = false;
            post.data.title = post.postTitle;
            post.data.body = post.postBody;
            post.tags = response.data.tag;
            post.data.is_changed = true;
        }else{
            this.show_create = false;
            post = new Post(response.data.post);
            post.id = post.data.id;
            post.tags = post.data.tag;
            this.feed.unshift(post);
        }
    });
}

export function delPost(post_number, id){
    var formData = new FormData();
    formData.append('id', id);
    url = '';       // del url
    makeAjaxRequest('post', url, formData)
        .then(response =>{
            this.show_del = false;
            delete this.feed.splice(post_number, 1);
        });
}

export function makeLike(post) {
    var formData = new FormData();
    formData.append('object_id', post.id);
    url = '';       // like url
    var ajax = makeAjaxRequest('post', url, formData);
    ajax.then(response => {
        post.data.is_liked = response.data.is_liked;
        post.data.likes_amount = response.data.amount
    });
}

                    // 4 COMMENTS
export function getComment(post) {
                        //post = this.feed[post_number];
    post.show_comments = !post.show_comments;
    if(post.show_comments){
        url = 'comment/post=' + post.id + '/';
        var a = makeAjaxRequest('get', url);
        a.then(response => {
            post.comments = response.data.comments;
        })
    }
}

export function postComment(post) {
    var formData = new FormData();
    //post = this.feed[post_number];
    if(post.commentInput === null || post.commentInput === '') {return}
    formData.append('post', post.id);
    formData.append('text', post.commentInput);
    url = 'comment/post=' + post.id +'/';
    var ajax = makeAjaxRequest('post', url, formData);
    ajax.then(response => {
        if (post.comments){
            post.comments.unshift(response.data.comment);
        }else{
            post.comments = [response.data.comment];
        }
        post.commentInput = '';
        post.data.comments_amount = response.data.comment.comments_amount;
    });
}

export function likeComment(post, comment_number){
    var formData = new FormData();
    formData.append('object_id', post.comments[comment_number].id);
    url = '';                         // like commrnt
    var ajax = makeAjaxRequest('post', url, formData);
    ajax.then( response =>{
        post.comments[comment_number].likes_amount = response.data.amount;
        post.comments[comment_number].is_liked = response.data.is_liked;
    });

}

export function delComment(post, comment_number){
    var formData = new FormData();
    formData.append('id', post.comments[comment_number].id);
    formData.append('post_id', post.id);
    url = '';           // del commment
    var ajax = makeAjaxRequest('post', url, formData);
    ajax.then(response => {
        delete post.comments.splice(comment_number, 1);
        post.data.comments_amount = response.data.comment_amount;
    });
}

export function showUpdateComment(post, comment_number){
    if(post.show_com_upd === comment_number){
        post.show_com_upd = '';
        post.updateInput = '';
    }else {
        post.show_com_upd = comment_number;
        post.updateInput = post.comments[comment_number].text;
    }
}

export function updateComment(post, comment_number){
    var formData = new FormData();
    //post = post = this.feed[post_number];
    formData.append('comment_id', post.comments[comment_number].id);
    formData.append('new_text', post.updateInput);
    url = '';                               // upd comment
    var ajax = makeAjaxRequest('post', url, formData);
    ajax.then(response => {
        post.comments[comment_number].text = post.updateInput;
        post.comments[comment_number].is_changed = true;
        post.show_com_upd = '';
        post.updateInput = '';
    });
}

export function showSettings(post){
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

export function changeSettings(post){
    var formData = new FormData();
    formData.append('post_id', post.id);
    formData.append('see_comments_permission', post.settings.see_comments_permission);
    formData.append('comment_permission', post.settings.comment_permission);
    formData.append('like_permission', post.settings['like_permission']);
    formData.append('repost_permission', post.settings['repost_permission']);
    formData.append('see_statistic_permission', post.settings['see_statistic_permission']);
    formData.append('see_author_permission', post.settings['see_author_permission']);
    formData.append('see_post_permission', post.settings['see_post_permission']);

    makeAjaxRequest('post', '', formData)                              // settings url
        .then(response =>{
            post.show_settings = false;
            post.show_upd = false;
        })

}

// 4 REPOSTS
function repostGet() { }
function getChats() { }
function repostToChat () { }
function repostToWall () { }

