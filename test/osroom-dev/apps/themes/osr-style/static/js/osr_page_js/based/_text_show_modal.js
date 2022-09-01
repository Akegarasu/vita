
     Vue.directive('highlight',function (el) {
      let blocks = el.querySelectorAll('pre code');
      blocks.forEach((block)=>{
        hljs.highlightBlock(block)
      })
    })

    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
            about_us:{},
            name:"",
      },
      filters: {
            formatDate: function (time) {
              return irrformatDate(time, "yyyy-MM-dd hh:mm");
            }
      }
    })

    // 加载完页面执行
    $(document).ready(function(){
        vue.name = $("#name").attr("content");
        get_global(vue.name);
        nav_active("head_li_"+vue.name);
    });

    function get_global(name){
        vue.name = name;
        var conditions = [
             {
                type:"text",
                names:[vue.name],
                result_key:"about_us"
             }
        ]
        var d ={
            conditions:JSON.stringify(conditions),
            theme_name:"osr-style"
        }

        var result = osrHttp("GET","/api/global/theme-data/display", d, args={not_prompt:true});
        result.then(function (r) {
            vue.about_us = r.data.medias.about_us[0];
        });
    }

