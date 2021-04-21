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

class ChatApp{
    constructor(){
        id;
        username;
        url;

    }
    // is_chat_exist = true;
    // chat = '';
    // user = {
    // 'id'= {{ request.user.id }},
    // 'username': '{{request.user.username}}',
    // 'role': 0
    // };
    // recipient= '';
    // //url:'{{ connection.get_chat_url }}',
    // messages: [],
    // chosenMessages: [],
    // messageInput: '',
    // updateInput: '',
    // change_chat_name_Input: '',
    //
    // users: [],
    // show_msg_del: true,
    // show_upd: false,
    // show_window: false,
    // show_add_new: false,
    // show_settings: false,
    // show_change_input: false,
    // friends: [],
    // chosen_friends: [],
    // settings: {},

created(){
    makeAjaxRequest('get', this.url)
        .then(response => {
            this.messages = response.data.messages;
            this.chat = response.data.chat;
            if(chat.is_public){
                response.data.users.forEach(user => {
                    this.users[user.id] = user;
                    if(user.id === this.user.id){this.user = user;}
                });
            }else{
                response.data.users.forEach(user => {
                    this.users[user.id] = user;
                    if(user.id === this.user.id){
                        this.user = user;
                    }else{
                        this.recipient = user;
                    }});
            }
        });
}

sendMessage(url, messageText=null) {
    var formData = new FormData();
    formData.append('chat', this.chat.id);
    if(messageText !== null){

        formData.append('text', messageText);
        formData.append('is_ancillary', true);
    }else{
        formData.append('text', this.messageInput);
        formData.append('is_ancillary', false);
    }
    makeAjaxRequest('post', url, formData)
        .then(response => {
            this.messages.push(response.data.new_message);
            this.messageInput = '';
            this.chosenMessages = [];
        })
}

selectMessage(index){
    var indexInList = this.chosenMessages.indexOf(this.messages[index]);

    if( indexInList === -1){
         if (!(this.messages[index].from_user === this.user.id) && this.user.role < this.chat.del_messages){
             this.show_msg_del = false;
         }
         this.chosenMessages.push(this.messages[index]);
    }else {
        if (!(this.messages[index].from_user === this.user.id || this.user.role < this.chat.del_messages)){
            this.show_msg_del = true;
        }
        if (this.chosenMessages.length === 1){
            this.show_upd = false
        }
        delete this.chosenMessages.splice(indexInList, 1);
    }
}

updateMessage(url) {
    var formData = new FormData();
    formData.append('message_id', this.chosenMessages[0].id);
    formData.append('text', this.updateInput);
    formData.append('user_id', this.user.id);
    var ajax = makeAjaxRequest('post', url, formData);
    ajax.then(response => {
        this.messages[this.chosenMessages[0].id].text = this.updateInput;
        this.chosenMessages = [];
        this.updateInput = '';
    })
}

deleteMessages(url) {
    var formData = new FormData();
    var list = this.chosenMessages.map(msg => {return msg.id});
    formData.append('chosenMessages', list);
    formData.append('chat_id', this.chat.id);
    var ajax = makeAjaxRequest('post', url, formData);
    ajax.then(response => {
        this.chosenMessages.forEach(msg =>{
            delete this.messages.splice(msg.id, 1);
        });
        this.chosenMessages = [];
    })
}

resendMessages () {}

show_add_newUser(url){
    this.show_add_new = !this.show_add_new;
    this.show_settings = false;
    if(this.show_add_new){
        var formData = new FormData();
        formData.append('chat', this.chat.id);
        makeAjaxRequest('get', url)
    .then(response => {
        this.friends = response.data.friends.filter(friend => {
            return this.users.map(user =>{return user.id}).indexOf(friend.id) === -1})
    });
    }
}

getParticipantsList(user_id) {
    let position_number = this.chosen_friends.indexOf(user_id);
    if(position_number === -1){
        this.chosen_friends.push(user_id);
    }else{
        delete this.chosen_friends.splice(position_number, 1)
    }
    if(this.chosen_friends.length === 1){
        this.is_public = false;
    }else if(this.chosen_friends.length > 1){
        this.is_public = true;
    }
}

addNewUser() {
    var formData = new FormData();
    formData.append('changes', 'add');
    formData.append('chat_id', this.chat.id);
    friends = this.chosen_friends.map(friend =>{ return friend.id });
    formData.append('friends', friends);
    makeAjaxRequest('post', this.url, formData)
        .then(response => {
            this.show_add_new = false;
            this.chosen_friends = [];
            response.data.new_users.forEach(user => {
                this.users[user.id] = user;
                this.sendMessage('user ' + user.username + ' join chat')
            });
        });
}

kickUser(user_id) {
    var formData = new FormData();
    formData.append('changes', 'kick');
    formData.append('chat_id', this.chat.id);
    if(user_id === -1){
        formData.append('user_id', this.user.id);
        this.sendMessage('user ' + this.user.username + ' leave chat');
    }else{
        formData.append('user_id', user_id);
        console.log(this.users[user_id]);
        this.sendMessage('user ' + this.users[user_id].username + ' was kicked');
        delete this.users.splice(user_id, 1);
    }
    makeAjaxRequest('post', this.url, formData);
}
addRemoveAdmin(user_id) {
    console.log(this.users);
    var formData = new FormData();
    formData.append('changes', 'admin');
    formData.append('chat_id', this.chat.id);
    formData.append('user_id', user_id);

    makeAjaxRequest('post', this.url, formData)
        .then(response =>{
            console.log(this.users);
            this.users[user_id].role = response.data.role;
            console.log(this.users[user_id].role);
            console.log(this.users)
        })
}

showSettings(){
    this.settings['see_messages'] = this.chat.see_messages;
    this.settings['send_messages'] = this.chat.send_messages;
    this.settings['del_messages'] = this.chat.del_messages;
    this.settings['add_new_users'] = this.chat.add_new_users;
    this.settings['remove_users'] = this.chat.remove_users;
    this.settings['add_remove_admins'] = this.chat.add_remove_admins;
    this.settings['see_admins'] = this.chat.see_admins;
    this.settings['change_chat_name'] = this.chat.change_chat_name;
    this.settings['change_chat_image'] = this.chat.change_chat_image;
}

changeSettings(){
    var formData = new FormData();
    formData.append('changes', 'settings');
    formData.append('chat_id', this.chat.id);
    formData.append('see_messages', this.settings['see_messages']);
    formData.append('send_messages', this.settings['send_messages']);
    formData.append('del_messages', this.settings['del_messages']);
    formData.append('add_new_users', this.settings['add_new_users']);
    formData.append('remove_users', this.settings['remove_users']);
    formData.append('add_remove_admins', this.settings['add_remove_admins']);
    formData.append('see_admins', this.settings['see_admins']);
    formData.append('change_chat_name', this.settings['change_chat_name']);
    formData.append('change_chat_image', this.settings['change_chat_image']);
}

changeChatName() {
    var formData = new FormData();
    new_chat_name = this.change_chat_name_Input;
    formData.append('changes', 'name');
    formData.append('chat_id', this.chat.id);
    formData.append('new_name', new_chat_name);
    makeAjaxRequest('post', this.url, formData)
        .then( r => {
            this.chat.chat_name = new_chat_name;
            this.show_window = false;
            this.show_add_new =  false;
            this.show_settings = false;
            this.show_change_input = false;
            this.sendMessage('chat name was changed on '+ new_chat_name);
        });
}

changeChatImage() {
    var formData = new FormData();
    formData.append('changes', 'img');
}

deleteChat (url) {
    var formData = new FormData();
    formData.append('chat_id', this.chat.id);
    makeAjaxRequest('post', url, formData).then(this.is_chat_exist = false)
}
}