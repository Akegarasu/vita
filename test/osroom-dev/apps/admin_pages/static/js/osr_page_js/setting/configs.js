    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{confs:[],
           projects:[],
           keyword:"",
           is_search_results:0,
           pages:[],
           page:1

      },
      filters: {
            formatDate: function (time) {

              return formatDate(time, "yyyy-MM-dd hh:mm");
            },
            formatKey: function (key) {
              return formatStr(key);
            }
      }
    });

    // 页面一加载完就自动执行
    $(document).ready(function(){


        var current_project = $("#project").attr("content");
        vue.current_project = current_project?current_project:vue.current_project;
        var keyword = $("#keyword").attr("content");
        vue.keyword = keyword?keyword:vue.keyword;
        var page = $("#page").attr("content");
        vue.page = page?page:vue.page;

        get_projects(vue.page, vue.keyword)
    });

    function get_projects(page, keyword){
        vue.keyword = keyword;
        vue.page = page;
        var d = {
            project_info:1,
            project_info_page:vue.page,
            project_info_pre:8,
            keyword:vue.keyword
        }
        if(vue.keyword){
            vue.is_search_results = 1
        }

       var result = osrHttp("GET","/api/admin/setting/sys/config",d, args={not_prompt:true});
       result.then(function (r) {
            vue.projects = r.data.projects;
            vue.pages = paging(page_total=vue.projects.page_total,
                            current_page=vue.projects.current_page);
        });
        var url = window.location.pathname+"?page="+vue.page;
        if(vue.keyword){
            url = url + "&keyword="+vue.keyword;
        }
        history_state(title=null,url=url);

    }


