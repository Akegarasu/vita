
    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
            content:"",
            routing:"",
           current_theme_name:null,
            url:""
            }
    })

    // 加载完页面执行
    $(document).ready(function(){
        var url_s = get_url_parameter();
        vue.current_theme_name = get_obj_value(url_s, "theme", null);
    })

    //当点击提交按钮,提交用于填入的数据到api
    function save(){
        formValidate();
        d = {
            routing:vue.routing,
            content:vue.content,
            theme_name: vue.current_theme_name
        }

        var result = osrHttp("POST","/api/admin/theme/page",d);
        result.then(function (r) {
            if(r.data.msg_type=="s"){
                window.open(r.data.url);
            }
        });
    }
