var vue = new Vue({
  el: '#app',
  delimiters:['{[', ']}'],
  data:{
        username:"",
        remember_me:0,
        code:null,
        code_url:null,
        code_url_obj:{},
        password:""}
})

// 页面一加载完就自动执行
$(document).ready(function(){
    var r = osrHttp("GET","/api/global");
    r.then(function (result) {
        if(result.data.is_authenticated){
            window.location.href = "/";
        }
    })

});

function sign_in(){
    formValidate();
    if (vue.remember_me){
        vue.remember_me = 1;
    }else{
        vue.remember_me = 0;
    }
    var d = {username:vue.username,
             password:vue.password,
             remember_me:vue.remember_me,
             code:vue.code,
             code_url_obj:JSON.stringify(vue.code_url_obj),
             next:get_url_parameter()["next"]
             };

     // 提交数据
     var result = osrHttp("PUT","/api/sign-in", d);
     result.then(function (r) {
            if(r.data.msg_type=="s"){
                window.location.href = r.data/to_url;

            }else if(r.data.open_img_verif_code){
                get_imgcode();
            }
     }).catch(function (r) {
        if(r.data.open_img_verif_code){
            get_imgcode();
        }
     });
}

function get_imgcode(){

    var result = osrHttp("GET","/api/vercode/image", {}, args={not_prompt:true});
    result.then(function (r) {
        if(r.data.msg_type == "s"){
            vue.code_url = r.data.code.url;
            vue.code_url_obj = r.data.code.img_url_obj;
        }
    })
}
