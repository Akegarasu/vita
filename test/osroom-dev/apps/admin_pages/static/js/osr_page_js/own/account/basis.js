 //当点击提交按钮,提交用于填入的数据到api
function save_basic(){
    if (vue.user_profile.custom_domain==-1){
        var d = {
                username:vue.user_profile.username,
                editor:vue.user_profile.editor}
    }else{
        var d = {
                 username:vue.user_profile.username,
                 custom_domain:vue.user_profile.custom_domain,
                 editor:vue.user_profile.editor
                 }
    }
    // 提交数据
    var result = osrHttp("PUT", "/api/account/basic", d);
    result.then(function (r) {
        if(r.data.msg_type=="s"){
            get_profile();
        }
    });

}