var vue = new Vue({
  el: '#app',
  delimiters:['{[', ']}'],
  data: {
    username:'',
    email:'',
    password: '',
    password2: '',
    email_code:"",
    //_send_code.html需要参数
    img_code_url_obj:{},
    img_code_url:"",
    img_code:""
  }
})

// 页面一加载完就自动执行
$(document).ready(function(){

    (function($) {
        if ($.AMUI && $.AMUI.validator) {
        // 增加多个正则
        $.AMUI.validator.patterns = $.extend($.AMUI.validator.patterns, {
             osrEmail:/^[a-zA-Z0-9_\-\.]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/,
             osrPassword:/^(?!(?:\d+|[a-zA-Z]+)$)[\da-zA-Z]{8,}$/
        });
        // 增加单个正则
        //$.AMUI.validator.patterns.osrEmail = /^[a-zA-Z0-9_\-\.]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/;
    }
    })(window.jQuery);

    var result = osrHttp("GET","/api/global");
    result.then(function (r) {
        if(r.data.is_authenticated){
            window.location.href = "/";
        }
    })
});

function sign_up(){
    formValidate();
    var d = {username:vue.username,
                email:vue.email,
                password:vue.password,
                password2:vue.password2,
                code:vue.email_code
            }
    // 提交数据
    osrHttp("POST","/api/sign-up", d);
}