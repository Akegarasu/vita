
    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
            content:"",
            file_relative_path:"",
            file_path:"",
           current_theme_name:null,
            filename:"",

            }
    })

    // 加载完页面执行
    $(document).ready(function(){

        vue.filename = $("#filename").attr("content");
        vue.file_path = $("#path").attr("content");
        var url_s = get_url_parameter();
        vue.current_theme_name = get_obj_value(url_s, "theme", null);
        get_content();

    })
    function get_content(){
        d = {
            file_path:vue.file_path,
            filename:vue.filename,
            theme_name: vue.current_theme_name
        }

        var result = osrHttp("GET","/api/admin/static/file",d, args={not_prompt:true});
       result.then(function (r) {
            vue.content = r.data.content;
            vue.file_relative_path = r.data.file_relative_path;

       });

    }

    //当点击提交按钮,提交用于填入的数据到api
    function save(){
        d = {
            file_path:vue.file_path,
            filename:vue.filename,
             theme_name: vue.current_theme_name,
            content:vue.content
        }
        osrHttp("PUT","/api/admin/static/file",d);

    }
