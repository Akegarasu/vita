    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
          emails:{datas:{}},
          email_view:{},
          status:"normal",
          status_list:{
                {{_("正常")}}:"normal",
                {{_("异常")}}:"abnormal",
                {{_("错误")}}:"error"
               },
          msg_type: "",
          msg_types: {
                {{_("所有")}}:"",
                {{_("安全码")}}:"code",
                {{_("通知")}}:"nt",
                {{_("其他")}}:"other"
          },
          keyword:"",
          checkAll:false,
          set:false,
          page:1,
          pages:{}
      },
      filters: {
            formatDate: function (time) {
              if(time){
                return formatDate(time, "yyyy-MM-dd hh:mm:ss");
              }
              return "";
            }
      }
    })

    // 加载完页面执行
    $(document).ready(function(){

        var status = $("#state").attr("content");
        vue.status = status?status:vue.status;
        var msg_type = $("#msg_type").attr("content");
        vue.msg_type = msg_type?msg_type:vue.msg_type;
        var page = $("#page").attr("content");
        vue.page = page?page:vue.page;
        var keyword = $("#keyword").attr("content");
        vue.keyword = keyword?keyword:vue.keyword

        get_emails(vue.status, vue.page, vue.msg_type, vue.keyword);
    })

    function get_emails(status, page, msg_type, keyword){
        vue.status = status;
        vue.page = page;
        vue.msg_type = msg_type;
        vue.keyword = keyword;
        d = {
            type:"email",
            page:page,
            status:status,
            msg_type:msg_type,
            keyword:keyword
        }

        var result = osrHttp("GET","/api/admin/message/email", d, args={not_prompt:true});
        result.then(function (r) {
            vue.emails = r.data.msgs;
            vue.checkAll = false;
            osr_check_all(vue.emails.datas, vue.checkAll, vue.set);
            vue.pages = paging(page_total=vue.emails.page_total,
                            current_page=vue.emails.current_page);
        });

        var url = window.location.pathname+"?page="+page+"&state="+vue.status+"&msg_type="+vue.msg_type;
        if(vue.keyword){
            url = url + "&keyword="+vue.keyword;
        }
        history_state(title=null,url=url);
    }

    function put_email_view(index){
        vue.email_view = vue.emails.datas[index];
    }

    function del_emails(){
        var ids = JSON.stringify(osr_get_checked_id());
        d = {
            ids:ids
        }
        var result = osrHttp("DELETE","/api/admin/message/email", d);
        result.then(function (r) {
            if(r.data.msg_type == "s"){
                get_emails(vue.status, vue.page, vue.msg_type, vue.keyword);
           }
        });

    }
