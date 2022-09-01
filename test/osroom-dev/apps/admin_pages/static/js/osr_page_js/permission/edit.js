    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{positions:"",
            per:"",
            purl:"/api/admin/permission"}
    })

    // 页面一加载完就自动执行
    $(document).ready(function(){

      var per_id = get_url_parameter()["id"];
      if (per_id){
          //获取per的信息
          var d = {"id":per_id};
          var result = osrHttp("GET",vue.purl, d, args={not_prompt:true});
            result.then(function (r) {
                vue.per = r.data.per;
            });
      }
      //获取权重剩余positions
      var result = osrHttp("GET","/api/admin/permission", {}, args={not_prompt:true});
      result.then(function (r) {
            vue.positions = r.data.positions;
      });
    });

    function save(){
        formValidate();
        var name = $("#name").val();
        var position = $("#positions").val();

        var info = $("#explain").val();
        var is_default = $("#is_default").is(":checked");
        if (is_default){
            is_default = 1;
        }else{
            is_default = 0;
        }
        if (vue.per){
            var per_id = vue.per._id;
            var d = {
                 name:name,
                 position:position,
                 explain:info,
                 is_default:is_default,
                 id:per_id
                 };
            // 修改
            osrHttp("PUT",vue.purl, d);

        }else{
            var d = {
                 name:name,
                 position:position,
                 explain:info,
                 is_default:is_default,
                 };
            //添加权限
            osrHttp("POST",vue.purl, d, {location_href:"/osr-admin/permission"});
        }
    }


