    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
        tokens:{},
        token_cnt:0,
      },
      filters: {
            formatDate: function (time) {
              return formatDate(time, "yyyy-MM-dd hh:mm");
            }
      }
    })

    // 加载完页面执行
    $(document).ready(function(){
         get_token();
    })

    function toggle_newly(index){

        if(vue.tokens[index].show_token=="******"){
            vue.tokens[index]["show_token"] = vue.tokens[index].token;
            vue.$set(vue.tokens, index, vue.tokens[index]);
            $("#toggle_newly_"+index).text('{{_("隐藏")}}');
            $("#toggle_newly_"+index).removeClass("fa fa-eye-slash");
            $("#toggle_newly_"+index).addClass("fa fa-eye");

        }else{
            vue.tokens[index]["show_token"] = "******";
            vue.$set(vue.tokens, index, vue.tokens[index]);
            $("#toggle_newly_"+index).text('{{_("显示")}}');
            $("#toggle_newly_"+index).removeClass("fa fa-eye");
            $("#toggle_newly_"+index).addClass("fa fa-eye-slash");
        }
    }

    function get_token(){

        var result = osrHttp("GET","/api/admin/token/secret-token", {},args={not_prompt:true});
        result.then(function (r) {
            vue.tokens = r.data.secret_token;
            vue.token_cnt = vue.tokens.length;
            $.each(vue.tokens, function(index,value){
                value["show_token"] = "******";
            });
        });
    }

    function created_new_token(){

        // 提交数据
         var result = osrHttp("POST","/api/admin/token/secret-token", {});
         result.then(function (r) {
            if(r.status=="success" && r.data.msg_type=="s"){
                get_token();
            }
         });
    }

    function activation_token(id){
        var d = {token_id:id, action:"activate"}
        var result = osrHttp("PUT","/api/admin/token/secret-token", d);
        result.then(function (r) {
            if (r.status=="success" && r.data.msg_type=="s"){
                get_token();
            }
        });
    }

    function disable_token(id){
        var d = {token_id:id, action:"disable"}
        var result = osrHttp("PUT","/api/admin/token/secret-token", d);
         result.then(function (r) {
            if(r.status=="success" && r.data.msg_type=="s"){
                get_token();
            }
         });
    }

    function delete_token(id){

        var d = {token_id:id}
        var result = osrHttp("DELETE","/api/admin/token/secret-token", d);
         result.then(function (r) {
            if(r.status=="success" && r.data.msg_type=="s"){
                get_token();
            }
         });
    }



