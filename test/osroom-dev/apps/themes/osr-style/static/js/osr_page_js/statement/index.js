
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
            statement:{},
            name:"user_agreement",
      },
      filters: {
            formatDate: function (time) {
              return irrformatDate(time, "yyyy-MM-dd hh:mm");
            }
      }
    })

    // 加载完页面执行
    $(document).ready(function(){
        var url_s = get_url_parameter()
        vue.name = get_obj_value(url_s,"s")
        get_global(vue.name);
        nav_active("head_li_"+vue.name);
    });

    function get_global(name){
        vue.name = name;
        var conditions = [
             {
                type:"text",
                names:[vue.name],
                result_key:"statement"
             }
        ]
        var d ={
            conditions:JSON.stringify(conditions),
            theme_name:"osr-style"

        }

        var result = osrHttp("GET","/api/global/theme-data/display", d, args={not_prompt:true});
        result.then(function (r) {
            vue.statement = r.data.medias.statement[0];
        });

        var url = window.location.pathname
                    +"?s="+vue.name
        history_state(null, url);
    }

