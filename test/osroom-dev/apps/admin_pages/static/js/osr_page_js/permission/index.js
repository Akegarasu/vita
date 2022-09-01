    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
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

      get_pers(vue.page);

    });

    function get_pers(page){

        vue.page = page;
        d = {
            page: page,
            pre: 15,
            is_details:1
        }
        var result = osrHttp("GET","/api/admin/permission", d, args={not_prompt:true});
        result.then(function (r) {
            vue.permissions = r.data.pers;
            vue.pages = paging(page_total=vue.permissions.page_total,
                            current_page=vue.permissions.current_page);
        });


        var url = window.location.pathname+"?page="+page;
        history_state(title=null,url=url);
    }

    function delete_per(id){
        data = {
            ids:JSON.stringify([id])
        }
        var result = osrHttp("DELETE","/api/admin/permission", data);
        result.then(function (r) {
            if(r.status == "success"){
                get_pers(1);
            }
        });
    }

