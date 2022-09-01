
    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
           msgs:{},
           msg_view:{},
           is_sys_msg:1,
           page:1,
           type:"notice",
           type_list:{
                '{{_("系统通知")}}':"notice",
                '{{_("其他")}}':"other"
               },
           pages:[],
           keyword:"",
           checkAll:false,
           set:false
      },
      filters: {
            formatDate: function (time) {
              return formatDate(time, "yyyy-MM-dd hh:mm");
            }
      }

    })
    // 加载完页面执行
    $(document).ready(function(){
        var type = $("#type").attr("content");
        vue.type = type?type:vue.type;
        var page = $("#page").attr("content");
        vue.page = page?page:vue.page;
        var sys = $("#sys").attr("content");
        vue.is_sys_msg = sys?parseInt(sys):vue.is_sys_msg;
        var keyword = $("#keyword").attr("content");
        vue.keyword = keyword?keyword:vue.keyword

        get_msgs(vue.page);
    });

    function get_msgs(page){
       vue.page = page;
       if(vue.type=="other"){
           var type = ["notice", "msg", "audit"];
       }else{
           var type = [vue.type];
       }
       var d = {
            is_sys_msg:vue.is_sys_msg,
            pre:10,
            type:JSON.stringify(type),
            page:vue.page,
            keyword:vue.keyword
       }

       var result = osrHttp("GET","/api/admin/message/on-site", d, args={not_prompt:true});
        result.then(function (r) {
            vue.msgs = r.data.msgs;
            vue.checkAll = false;
            osr_check_all(vue.msgs.datas, vue.checkAll, vue.set);
            vue.pages = paging(page_total=vue.msgs.page_total,
                                current_page=vue.msgs.current_page);
        });
        var url = window.location.pathname+"?type="+vue.type+"&page="+page+"&sys="+vue.is_sys_msg;
        if(vue.keyword){
            url = url + "&keyword="+vue.keyword;
        }
        history_state(title=null,url=url);


    }

    function del_msgs(){
       var ids = JSON.stringify(osr_get_checked_id());
       var d = {
            ids:ids
       }

       var result = osrHttp("DELETE","/api/admin/message/on-site", d);
        result.then(function (r) {
            if(r.data.msg_type == "s"){
                get_msgs(vue.page);
           }
        });

    }

    function switch_type(type){
        if(type=="other"){
            vue.type = type;
            vue.is_sys_msg = 0;
        }else{
            vue.type = "notice";
            vue.is_sys_msg = 1;
        }
        vue.keyword = "";
        get_msgs(1);
    }

    function put_msg_view(index){
        vue.msg_view = vue.msgs.datas[index];
    }

