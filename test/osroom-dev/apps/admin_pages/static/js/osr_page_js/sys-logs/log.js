    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{logs:""},
      pages:{},
      page:1,
      log_name:"",
      host_ip:""
    })

    // 页面一加载完就自动执行
    $(document).ready(function(){
        page = $("#page").attr("content");
        vue.page = page?page:vue.page;
        get_logs(vue.page);
    });

    function get_logs(page){
        vue.log_name = $("#name").attr("content");
        vue.host_ip = $("#ip").attr("content");
        d = {
            name:vue.log_name,
            page:page,
            ip:vue.host_ip
        }

        var result = osrHttp("GET","/api/admin/setting/sys/log",d, args={not_prompt:true});
       result.then(function (r) {
            vue.logs = r.data.logs;
            vue.pages = paging(page_total=vue.logs.page_total,
                                current_page=vue.logs.current_page);
       });

        var url = window.location.pathname+"?page="+page+"&name="+vue.log_name+"&ip="+vue.host_ip;
        history_state(title=null,url=url);
    }


