
    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
            photo:{user:{avatar_url:"", follow:{}}},
            mid:"",
            inform:{}
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
        vue.mid = get_obj_value(url_s,"mid")
        get_global();
    });

    function get_global(){
        var d ={
            media_id:vue.mid
        }
        var result = osrHttp("GET","/api/global/media", d, args={not_prompt:true});
        result.then(function (r) {
            vue.photo = r.data.media;
        });
    }

    //初始化图片查看器
    var is_init_viewer = false;
    function init_viewer(id) {
        id = id?id:"galley";
        if(!is_init_viewer){
            var $images = $('#'+id);
            $images.on({}).viewer({
                navbar:false,
            });
            is_init_viewer = true;
        }
        $('#'+id).on({}).viewer('update');
    }

