    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data: {
        username:'',
        email:'',
        password: '',
        password2: '',
        email_code:"",
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
    });

   function sign_up(){
        formValidate();
        var d = {
            username:vue.username,
            email:vue.email,
            password:vue.password,
            password2:vue.password2
        }
        // 提交数据
        result = osrHttp("POST","/api/admin/user", d);
        result.then(function (r) {
            if(r.data.msg_type == "s"){
                window.location.href = "/osr-admin/user?status={{data.fs}}&page={{data.fp}}";
            }
        })
   }

