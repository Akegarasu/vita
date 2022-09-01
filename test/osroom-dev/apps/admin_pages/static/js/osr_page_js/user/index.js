    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{users:"",
            keyword:"",
            status:"normal",
            status_list:{
                '{{_("正常")}}':"normal",
                '{{_("未激活")}}':"inactive",
                '{{_("已移除")}}':"cancelled",
               },

             checkAll:false,
            set:false,
            user_view:{user_op_log:[],
                         user_login_log:[],
                         _id:"",
                         inform:{update_time:null,
                         total:0}
                         },
            pages:{},
            page:1
      },
      filters: {
            formatDate: function (time) {
              return formatDate(time, "yyyy-MM-dd hh:mm:ss");
            },
            Reverse: function (list) {
              return reverse(list);
            }
      }
    })

    // 加载完页面执行
    $(document).ready(function(){
         var status = $("#state").attr("content");
        vue.status = status?status:vue.status;
        var page = $("#page").attr("content");
        vue.page = page?page:vue.page;
        var keyword = $("#keyword").attr("content");
        vue.keyword = keyword?keyword:vue.keyword;

        get_users(vue.status,vue.page,vue.keyword);
    })

    function get_users(status, page, keyword ){
        vue.keyword = keyword;
        vue.status = status;
        vue.page = page;
        d = {
            status:status,
            keyword:keyword,
            page:page,
            pre:10
        }

        var result = osrHttp("GET","/api/admin/user",d,args={not_prompt:true});
        result.then(function (r) {
             vue.users = r.data.users;
            vue.status = r.data.status;
            vue.checkAll = false;
            osr_check_all(vue.users.datas, vue.checkAll, vue.set);
            put_user_view(0);
            vue.pages = paging(page_total=vue.users.page_total,
                                current_page=vue.users.current_page);
        });

        var url = window.location.pathname+"?page="+page+"&state="+vue.status;
        if(vue.keyword){
            url = url + "&keyword="+vue.keyword;
        }
        history_state(title=null,url=url);

    }

    function put_user_view(index){
        vue.user_view = vue.users.datas[index];

    }
    function activation_user(active){

        ids = JSON.stringify(osr_get_checked_id());
        var d = {
                 ids:ids,
                 op:"activation",
                 active:active
                 };
        // 提交数据
        var result = osrHttp("PUT","/api/admin/user", d);
        result.then(function (r) {
            if(r.data.msg_type=='s'){
                get_users(vue.status, vue.page, vue.keyword );
            }
        });
    }


    function delete_user(permanent){
        var ids = new Array();
        $("input:checkbox[type='checkbox']:checked").each(function(){
             if($(this).val() != 'on'){
                ids.push($(this).val());
               }
        })
        ids = JSON.stringify(ids);

        if(parseInt(permanent)){
            var d = {
                 ids:ids,
                 permanent:1
            };
            var url = "/api/admin/user/del"
        }else{
            var d = {
                 ids:ids,
            };
            var url = "/api/admin/user"
        }
        // 提交数据
        var result = osrHttp("DELETE",url, d);
        result.then(function (r) {
            if(r.data.msg_type=='s'){
                get_users(vue.status, vue.page, vue.keyword );
            }
        });
    }

    function restore_user(){
        var ids = new Array();
        $("input:checkbox[type='checkbox']:checked").each(function(){
            if($(this).val() != 'on'){
             ids.push($(this).val());
             }
        })
        ids = JSON.stringify(ids);
        var d = {
                 ids:ids,
                 op:"restore"
                 };
        // 提交数据
        var result = osrHttp("PUT","/api/admin/user", d);
        result.then(function (r) {
           if(r.data.msg_type=='s'){
                get_users(vue.status, vue.page, vue.keyword );
            }
        });
    }

