    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{permissions:"",
            role:"",
            purl:"/api/admin/role"}
    })

    // 页面一加载完就自动执行
    $(document).ready(function(){

      var role_id = $("#role_id").attr("content");
      if (role_id){
          //获取role的信息
          var d = {"id":role_id};
          var result = osrHttp("GET",vue.purl, d, args={not_prompt:true});
            result.then(function (r) {
                vue.role = r.data.role;
            });
      }
      //获取权重数据,遍历添加到select标签
      var result = osrHttp("GET","/api/admin/permission", {}, args={not_prompt:true});
      result.then(function (r) {
            vue.permissions = r.data.permissions;
      });
    });

    function save(){
        formValidate();
        var name = $("#name").val();
        var permissions = $("#permissions").val();

        var info = $("#info").val();
        var is_default = $("#default").is(":checked");
        if (is_default){
            is_default = 1;
        }else{
            is_default = 0;
        }
        if (vue.role){
            var role_id = vue.role._id;
            var d = {
                 name:name,
                 permissions:JSON.stringify(permissions),
                 instructions:info,
                 default:is_default,
                 id:role_id
                 };
            // 修改权限
            osrHttp("PUT",vue.purl, d, {location_href:"/osr-admin/role"});

        }else{
            var d = {
                 name:name,
                 permissions:JSON.stringify(permissions),
                 instructions:info,
                 default:is_default,
                 };
            //添加权限
            osrHttp("POST",vue.purl, d, {location_href:"/osr-admin/role"});
        }
    }


