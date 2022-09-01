    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{roles:"",
            user:"",
            password:"",
            edit_password:false,
            role_id:"",
            active:"",
            purl:"/api/admin/user"
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

      var user_id = $("#user_id").attr("content");
      if (user_id){
          //获取role的信息
          vue.purl = "/api/admin/user";
          var d = {"id":user_id};

          var result = osrHttp("GET","/api/admin/user", d,args={not_prompt:true});
          result.then(function (r) {
                vue.user = r.data.user;
          });
      }
      //获取权重数据,遍历添加到select标签
      var result = osrHttp("GET","/api/admin/role",{},args={not_prompt:true});
        result.then(function (r) {
            vue.roles = r.data.roles;
        });
    });
    function edit_pass() {
        vue.edit_password = !vue.edit_password;
    }
    //当点击提交按钮,提交用于填入的数据到api
    function save(){
        var role_id = $("#role").val();
        var active = $("#active").is(":checked");
        if (active){
            active = 1;
        }else{
            active = 0;
        }
        var d = {
                 id:vue.user._id,
                 role_id:role_id,
                 email: vue.user.email,
                 password: vue.password,
                 active:active
                 };
        // 提交数据
        var result = osrHttp("PUT",vue.purl, d);
    }

