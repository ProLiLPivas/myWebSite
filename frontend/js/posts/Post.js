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
    repostInput = '';
    show_upd = false;
    show_del = false;
    show_settings = false;
    show_repost = false;
    repost_type = 0;

    chats4repost = [];
    selected2repost = [];

    tagInput = '';
    show_tag_input = false;
    attachedTags = [];
}

export { Post };