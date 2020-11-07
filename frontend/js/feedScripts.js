class Post{
    constructor(data=null){
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
    commentInput = '';
    show_com_upd = '';
    updateInput = '';
    show_upd = false;
    show_rep = false;
    show_del = false;
    tagInput = '';
    show_tag_input = false;
    is_liked = false;
    attachedTags = [];
                //selected_field: null,
}

new Vue({
    el: '#start_page',
    data: {
        show_create: false,
        newPost: [],
        feed: [],
        user: {},
    },
    created(url){
        //url = '{%  url 'get_feed_url' %}';
        makeAjaxRequest('get', url)
            .then(response =>{
                this.feed = response.data.posts.map(function(post){
                    return  new Post(post);
                });
                this.user = response.data.user;
            });
        }, methods: {
                    // 4 POST
        attachTag: function (post) {
            if(post.attachedTags.indexOf(post.tagInput) === -1){
                post.attachedTags.push(post.tagInput);
            }
            },
        unattachTag: function(post, index) {
            delete post.attachedTags.splice(index, 1)
        },
        startCreatingPost: function(){
            this.show_create = !this.show_create;
            if(this.show_create){
                this.newPost = [new Post()]
            }else {
                this.newPost = null
            }
            },
        showUpdatePost: function(post){
            post.show_upd = !post.show_upd;
            if(post.show_upd){
                post.postTitle = post.data.title;
                post.postBody = post.data.body;
                post.attachedTags = post.tags.map(tag =>{ return tag.title});
            }
        },
        // create_or_updatePost: function (post, is_update=false) {
        //     var formData = new FormData();
                    //     formData.append('title', post.postTitle);
                    //     formData.append('body', post.postBody);
                    //     formData.append('tags', post.attachedTags);
                    //     formData.append('is_update', is_update);
                    //     formData.append('post_id', post.id);
                    //     if(is_update){url = '{% url 'update_post_url' %}'}
                    //     else {url = '{% url 'create_post_url' %}'}
                    //     var ajax = makeAjaxRequest('post', url , formData);
                    //     ajax.then(response =>{
                    //         if(is_update){
                    //             post.show_upd = false;
                    //             post.data.title = post.postTitle;
                    //             post.data.body = post.postBody;
                    //             post.tags = response.data.tag;
                    //         }else{
                    //             this.show_create = false;
                    //             post.data = response.data.post;
                    //             post.id = post.data.id;
                    //             post.tags = post.data.tag;
                    //             this.feed.unshift(post);
                    //
                    //         }
                            //
                            //post.tags = response.data.tags
                    //     });
                    // },
    delPost: function(url, post_number, id){
        var formData = new FormData();
        formData.append('id', id);
        //url = '{% url 'delete_post_url' %}';
        makeAjaxRequest('post', url, formData)
            .then(response =>{
                this.show_del = false;
                delete this.feed.splice(post_number, 1);
            });
        },
    makeLike: function (url , post) {
        var formData = new FormData();
        formData.append('object_id', post.id);
        // url = '{% url 'like_post_url' %}';
        var ajax = makeAjaxRequest('post', url, formData);
        ajax.then(response => {
            post.is_liked = response.data.is_liked;
            post.data.likes_amount = response.data.amount
        });
    },

                    // 4 COMMENTS
                    getComment: function (post) {
                        //post = this.feed[post_number];
                        post.show_comments = !post.show_comments;
                        if(post.show_comments){
                            url = 'comment/post=' + post.id + '/';
                            var a = makeAjaxRequest('get', url);
                            a.then(response => {
                                post.comments = response.data.comments;
                            })
                        }
                    },

                    postComment: function(post) {
                        var formData = new FormData();
                        //post = this.feed[post_number];
                        if(post.commentInput === null || post.commentInput === '') {return}
                        formData.append('post', post.id);
                        formData.append('text', post.commentInput);
                        url = 'comment/post=' + post.id +'/';
                        var ajax = makeAjaxRequest('post', url, formData);
                        ajax.then(response => {
                            if (post.comments){
                                post.comments.unshift(response.data.comments);
                            }else{
                                post.comments = [response.data.comments];
                            }
                            post.commentInput = '';
                            post.data.comments_amount = response.data.comment_amount ;

                        });
                    },

                    likeComment: function(url, post, comment_number){
                        var formData = new FormData();
                        formData.append('object_id', post.comments[comment_number].id);
                        // url = '{% url 'like_comment_url' %}';
                        var ajax = makeAjaxRequest('post', url, formData);
                        ajax.then( response =>{
                            post.comments[comment_number].likes_amount = response.data.amount
                        });
                    },
                    delComment: function(url, post, comment_number){
                        var formData = new FormData();
                        formData.append('id', post.comments[comment_number].id);
                        formData.append('post_id', post.id);
                        // url = '{% url 'delete_comment_url' %}';
                        var ajax = makeAjaxRequest('post', url, formData);
                        ajax.then(response => {
                            delete post.comments.splice(comment_number, 1);
                             post.data.comments_amount = response.data.comment_amount;

                        });
                    },
                    showUpdateComment: function(post, comment_number){
                        if(post.show_com_upd === comment_number){
                            post.show_com_upd = '';
                            post.updateInput = '';
                        }else {
                           post.show_com_upd = comment_number;
                           post.updateInput = post.comments[comment_number].text;
                        }
                    },
                    updateComment: function(url, post, comment_number){
                        var formData = new FormData();
                        //post = post = this.feed[post_number];
                        formData.append('comment_id', post.comments[comment_number].id);
                        formData.append('new_text', post.updateInput);
                        //url = '{% url 'update_comment_url' %}';

                        var ajax = makeAjaxRequest('post', url, formData);
                        ajax.then(response => {
                            post.comments[comment_number].text = post.updateInput;
                            post.show_com_upd = '';
                            post.updateInput = '';
                        });
                    },


                    // 4 REPOSTS
                    repostGet: function () { },
                    getChats: function () { },
                    repostToChat: function () { },
                    repostToWall: function () { },
                }
});