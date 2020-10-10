export function makeAjaxRequest(method, url, data=null)
{
     return axios({
         method: method,
         url: url,
         data: data,
         xsrfCookieName: 'csrftoken',
         xsrfHeaderName: 'X-CSRFToken',
         headers :{
             'Access-Control-Allow-Origin': '*',
         },
     });
}


export function getComment(instance, url)
{
    instance.show_comments = !instance.show_comments;
    if(instance.show_comments){
        axios
            .get(url)
            .then(response => {
                var r = response.data.comments;
                instance.comments = r;
            });
    }
}

export function postComment(instance, url)
{
    var formData = new FormData();
    if(instance.inputText === null || instance.inputText === '') {return}
    formData.append('post', instance.post_id);
    formData.append('text', instance.inputText);

    var ajax = makeAjaxRequest('post', url, formData);
    ajax.then(response => {
        if (instance.comments){
            instance.comments.push(response.data.comments);
            instance.inputText = '';
        }else{
            instance.comments = [ response.data.comments ];
            instance.inputText = '';
        }
    });
}

export function delPost(instance, url)
{
    var formData = new FormData();
    formData.append('post', instance.post_id);
    var ajax = makeAjaxRequest('post', url, formData);
    ajax.then(
        instance.show_del = false
    );
}
export function updatePost(){

}

export function makeLike(instance, url)
{
    var formData = new FormData();
    formData.append('post', instance.post_id);

    var a = axios({
        method: 'post',
        url: uri,
        data: formData,
        xsrfCookieName: 'csrftoken',
        xsrfHeaderName: 'X-CSRFToken',
        headers: {
            'Access-Control-Allow-Origin': '*',
        },

    });
    console.log(a);
    var ajax = makeAjaxRequest('post', url, formData);
}

