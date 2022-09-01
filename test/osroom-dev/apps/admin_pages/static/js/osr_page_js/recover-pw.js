var vue = new Vue({
  el: '#app',
  delimiters:['{[', ']}'],
  data: {
    email:'',
    password: '',
    password2: '',
    email_code:"",
    //_send_code.html需要参数
    send_code_to_exist_account:1,
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

function reset(){
    formValidate();
    var d = {   email:vue.email,
                password:vue.password,
                password2:vue.password2,
                email_code:vue.email_code,
            }
    // 提交数据
    osrHttp("PUT","/api/account/password/retrieve", d);
}