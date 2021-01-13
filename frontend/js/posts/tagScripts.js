function getTagUrl(tag){
    return 'tag=' + tag.title + '/'
}

function attachTag(post) {
    var len = post.tagInput.length -1 ;
    if(post.tagInput[len]){
        while (post.tagInput[len] === ' '){
            post.tagInput = post.tagInput.slice(0, -1);
            len -= 1;
        }
    }
    console.log(post.tagInput.length);
    if((post.tagInput.indexOf(' ') === -1 ) && post.tagInput!== ''){
        if(post.attachedTags.indexOf(post.tagInput) === -1){
            post.attachedTags.push(post.tagInput);
            post.tagInput = '';
        }
    }
}

function unattachTag(post, index) {
    delete post.attachedTags.splice(index, 1)
}

export { getTagUrl, attachTag, unattachTag }