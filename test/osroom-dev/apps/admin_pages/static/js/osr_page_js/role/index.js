    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
       roles:"",
       permissions:"",
       page:1,
       pages:{}
      },

    })
    // 页面一加载完就自动执行
    $(document).ready(function(){
      //获取权重数据,遍历添加到select标签
      var page = $("#page").attr("content");
       vue.page = page?page:vue.page;

      get_roles(vue.page);

    });

    function get_roles(page){

        vue.page = page;
        d = {
            page: page,
            pre: 10
        }
        var result = osrHttp("GET","/api/admin/role", d, args={not_prompt:true});
        result.then(function (r) {
            vue.roles = r.data.roles;
            vue.pages = paging(page_total=vue.roles.page_total,
                            current_page=vue.roles.current_page);
            //获取全部
            var result2 = osrHttp("GET","/api/admin/permission", {}, args={not_prompt:true});
            //result2.then(function (pers) {
            //    vue.$forceUpdate();
            //});

        });


        var url = window.location.pathname+"?page="+page;
        history_state(title=null,url=url);
    }

    function delete_role(id){
        data = {
            ids:JSON.stringify([id])
        }
        var result = osrHttp("DELETE","/api/admin/role", data);
        result.then(function (r) {
            if(r.status == "success"){
                get_roles(1);
            }
        });
    }

