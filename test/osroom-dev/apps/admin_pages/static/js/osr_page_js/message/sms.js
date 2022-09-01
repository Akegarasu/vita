    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
          smss:{datas:{}},
          sms_view:{},
          status:"normal",
          status_list:{
                '{{_("正常")}}':"normal",
                '{{_("异常")}}':"abnormal",
                '{{_("错误")}}':"error"
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
        var page = $("#page").attr("content");
        vue.page = page?page:vue.page;
        var keyword = $("#keyword").attr("content");
        vue.keyword = keyword?keyword:vue.keyword

        get_smss(vue.status, vue.page, vue.keyword);
    })

    function get_smss(status, page, keyword){
        vue.status = status;
        vue.page = page;
        vue.keyword = keyword;
        d = {
            type:"sms",
            page:page,
            status:status,
            keyword:keyword
        }

        var result = osrHttp("GET","/api/admin/message/sms", d, args={not_prompt:true});
        result.then(function (r) {
            vue.smss = r.data.msgs;
            vue.checkAll = false;
            osr_check_all(vue.smss.datas, vue.checkAll, vue.set);
            vue.pages = paging(page_total=vue.smss.page_total,
                            current_page=vue.smss.current_page);
        });
        var url = window.location.pathname+"?page="+page+"&state="+vue.status;
        if(vue.keyword){
            url = url + "&keyword="+vue.keyword;
        }
        history_state(title=null,url=url);
    }

    function put_sms_view(index){
        vue.sms_view = vue.smss.datas[index];
    }

    function del_smss(){
        var ids = JSON.stringify(osr_get_checked_id());
        d = {
            ids:ids
        }

        var result = osrHttp("DELETE","/api/admin/message/sms", d);
        result.then(function (r) {
            if(r.data.msg_type == "s"){
                get_smss(vue.status, vue.page, vue.keyword);
           }
        });

    }


