
    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
            users:{kw:"", items:[]},
            posts:{kw:"", items:[]},
            pages:[],
            page:1,
            keyword:"",
            target:"",
            search_logs: null
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
        get_search_logs();
        vue.keyword = get_obj_value(url_s, "s");
        vue.target = get_obj_value(url_s, "t", "post");
        vue.page = get_obj_value(url_s, "page", 1);
        global_search(vue.keyword, vue.target, vue.page);
        nav_active("head_li_"+vue.target);

    })

    function get_search_logs(){
        var result = osrHttp("GET","/api/search/logs", args={not_prompt:true});
        result.then(function (r) {
            vue.search_logs = r.data.logs;
        });
    }
    function clear_logs(){
        var result = osrHttp("DELETE","/api/search/logs", args={not_prompt:true});
        result.then(function (r) {
            vue.search_logs = [];
        });
    }
    function global_search(keyword, target, page){

        vue.keyword = keyword;
        vue.target = target;
        vue.page = page;
        
        var url = window.location.pathname
                    +"?s="+keyword
                    +"&page="+page
        if(vue.target){
            url = url+'&t='+vue.target;
        }
        history_state(null, url);
        if(!vue.keyword){
            return 0;
        };

        //if(vue.target=="post" && vue.posts.kw == keyword){
        //    return 0;
        //}else if(vue.target=="user" && vue.users.kw == keyword){
        //    return 0;
        //}

        vue.target = target;
        vue.page = page;
        d = {
            keyword:keyword,
            page:vue.page
        }
        if(target){
            d["target"] = target;
        }
        var result = osrHttp("GET","/api/search", d, args={not_prompt:true});
        result.then(function (r) {
            if(!$.isEmptyObject(r.data.posts)){
                vue.posts = r.data.posts;

                vue.pages = paging(page_total=r.data.posts.items.page_total,
                                    current_page=r.data.posts.items.current_page);
            }
            if(!$.isEmptyObject(r.data.users)){
                vue.users = r.data.users;
                vue.pages = paging(page_total=r.data.users.items.page_total,
                                    current_page=r.data.users.items.current_page);
            }
            get_search_logs();
        });

        
    }
