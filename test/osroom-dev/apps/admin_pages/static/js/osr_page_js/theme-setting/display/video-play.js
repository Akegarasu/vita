    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
        media:{}
      }
    });

    // 加载完页面执行
    $(document).ready(function(){
        get_media();
    });

    function get_media(){
        var d = {
            theme_name: vue.current_theme_name,
            id:$("#id").attr("content"),
        }

        var result = osrHttp("GET","/api/admin/theme/display-setting", d, args={not_prompt:true});
        result.then(function (r) {
            vue.media = r.data.media;
        });
    }
