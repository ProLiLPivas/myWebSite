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
export { makeAjaxRequest };
