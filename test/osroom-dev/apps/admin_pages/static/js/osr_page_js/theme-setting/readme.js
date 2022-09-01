
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
            readme:{},
            name:""
      },
      filters: {
            formatDate: function (time) {
              return irrformatDate(time, "yyyy-MM-dd hh:mm");
            }
      }
    })

    // 加载完页面执行
    $(document).ready(function(){
        var url_s = get_url_parameter();
        vue.name = get_obj_value(url_s, "name");
        get_readme(vue.name);
    });

    function get_readme(name){

        var d ={
            name:name
        }

        var result = osrHttp("GET","/api/admin/theme", d, args={not_prompt:true});
        result.then(function (r) {
            vue.readme = r.data.readme;
            vue.readme = marked(vue.readme);
        });
    }

