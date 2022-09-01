
    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
          urls:{datas:{} },

          types:[
                    ["{{_('所有')}}", "all"],
                    ["{{_('ApiUrl')}}", "api"],
                    ["{{_('页面路由')}}", "page"]
                 ],
          keyword:"",
          current_type:"all",
          page:1,
          pages:{},
          permissions:[]
      }
    })

    // 加载完页面执行
    $(document).ready(function(){
        var temp_page = $("#page").attr("content");
        vue.page =  temp_page?temp_page:vue.page;
        var temp_keyword = $("#keyword").attr("content");
        vue.keyword =  temp_keyword?temp_keyword:vue.keyword;
        vue.current_type = $("#type").attr("content");
        get_urls(vue.page, vue.keyword);
    })

    function get_urls(page, kw){
        vue.page = page;
        vue.keyword = kw;
        d = {
            page:vue.page,
            keyword:vue.keyword
        }
        if(vue.current_type != "all" && vue.current_type){
            d["type"] = vue.current_type;
        }

        var result = osrHttp("GET","/api/admin/url/permission", d, args={not_prompt:true});
        result.then(function (r) {
            vue.urls = r.data.urls;
            vue.pages = paging(page_total=vue.urls.page_total,
                            current_page=vue.urls.current_page);
        });

        var url = window.location.pathname+"?page="+page+"&type="+vue.current_type;
        if(vue.keyword){
            url += "&keyword="+vue.keyword;
        }
        history_state(title=null,url=url);

        //permission

        var result2 = osrHttp("GET","/api/admin/permission", {}, args={not_prompt:true});
        result2.then(function (r) {
            vue.permissions = r.data.permissions;
            vue.cnt = vue.permissions.length;
            vue.permissions = r.data.permissions;
        });
    }

    function del_url(id){
         d = {
            ids:JSON.stringify([id])
        }
        var result = osrHttp("DELETE","/api/admin/url/permission", d);
        result.then(function (r) {
            if (r.status=="success" && r.data.msg_type=="s"){
                 get_urls(vue.page, vue.keyword);
            }
        });
    }

    function switch_type(page, v){
        vue.current_type = v;
        get_urls(page, "");
        history_state(title=null,url="/osr-admin/permission/url?page="+page+"&type="+v);
    }
