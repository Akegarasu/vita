
    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
           msgs:{content:{}},
           type:"notice",
           label:null,
           status_update:"have_read",
           page:1,
           pages:[],
           unread:{"notice":0, "comment":0}
      },
      filters: {
            formatDate: function (time) {
              return irrformatDate(time, "yyyy-MM-dd hh:mm");
            }
      }

    })

    // 加载完页面执行
    $(document).ready(function(){

        var type = $("#type").attr("content");
        vue.type = type?type:vue.type;
        var page = $("#page").attr("content");
        vue.page = page?page:vue.page;

        nav_active("head_li_"+vue.type, vue.type);
        get_msgs(vue.page);
    });

    function get_msgs(page){

        vue.page = page;
        //type
        if(vue.type == 'private_letter'){
             var type = ['private_letter'];

        }else if(vue.type == 'comment'){
             var type = ['notice'];
             vue.label = ['comment']
        }else{
            var type = ['notice'];
            vue.label = ["sys_notice", "audit_failure"];
        }

        //label

       vue.page = page;
       var d = {
            type:JSON.stringify(type),
            pre:10,
            page:vue.page,
            status_update:"have_read"
       }
       if(vue.label){
            d['label'] = JSON.stringify(vue.label);
       }

       var result = osrHttp("GET","/api/user/message", d, args={not_prompt:true});
        result.then(function (r) {
            vue.msgs = r.data.msgs;
            vue.pages = paging(page_total=vue.msgs.page_total,
                                current_page=vue.msgs.current_page);

            vue.unread["notice"] = 0;
            vue.unread["comment"] = 0;
            $.each(vue.msgs.more, function(index, value){
                if(index=="comment"){
                    vue.unread["comment"] += value["unread"];
                }else if(index=="private_letter"){
                    vue.unread["private_letter"] += value["unread"];
                }else{
                    vue.unread["notice"] += value["unread"];
                }

            });
        });

        var url = window.location.pathname+"?type="+vue.type+"&page="+vue.page;
        history_state(null, url);
    }

    function del_msgs(id){

       var d = {
            ids:JSON.stringify([id]),
       }
       var result = osrHttp("DELETE","/api/user/message", d);
        result.then(function (r) {
            if(r.data.msg_type == "s"){
                get_msgs(vue.page);
           }
        });
    }

    function switch_type(type){
        vue.type = type;
        get_msgs(1);
    }

    //回复comment
    function reply_trigger(id){
        $("#"+id).toggle();
    }
    function reply_comment(target_type, target_id, reply_id, reply_user_id, reply_username, input_id){
        var d = {
            content:$("#"+input_id).val(),
            target_type:target_type,
            target_id:target_id,
            reply_id:reply_id,
            reply_user_id:reply_user_id,
            reply_username:reply_username
        }
        osrHttp("POST","/api/comment",d);

    }

