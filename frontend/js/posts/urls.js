class UrlsList{
    static urlsList = {
        getFeedUrl: '/feed/',
        getPostUrl: '/feed/post={post_id}/',
        cretePostUrl: '/feed/post/create/',
        updatePostUrl: '/feed/post/update/',
        deletePostUrl: '/feed/post/delete/',
        postSettingsUrl: '/feed/post/permissions/',
        likePostUrl: '/feed/like/',
        commentUrl: '/feed/comment/post={post_id}/',
        updateCommentUrl: '/feed/comment/update/',
        deleteCommentUrl: '/feed/comment/delete/',
        likeCommentUrl: '/feed/comment/like/',
    }
}

export { UrlsList }