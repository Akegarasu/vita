
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
            notice:{},
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
        vue.name = get_obj_value(url_s,"n")
        get_global(vue.name);
    });

    function get_global(name){
        vue.name = name;
        var conditions = [
             {
                type:"text",
                names:[vue.name],
                result_key:"notice",
                theme_name:"osr-style"
             }
        ]
        var d ={
            conditions:JSON.stringify(conditions)

        }

        var result = osrHttp("GET","/api/global/theme-data/display", d, args={not_prompt:true});
        result.then(function (r) {
            vue.notice = r.data.medias.notice[0];
        });

        var url = window.location.pathname
                    +"?n="+vue.name
        history_state(null, url);
    }

