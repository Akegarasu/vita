
    //获取comment
    function get_comment(sort, page){

        if(sort=="t-desc"){
            sort = [{"issue_time":-1}];
        }else if(sort=="t-asc"){
            sort = [{"issue_time":1}];
        }else{
            sort = [{"like": -1}, {"issue_time": -1}];
        }

        if(!page){
            page = 1
        }

        d = {
            target_id:vue.post_id,
            sort:JSON.stringify(sort),
            page:page,
            pre:10
        }

        var result = osrHttp("GET","/api/comment", d, args={not_prompt:true});
        result.then(function (r) {
            vue.comments = r.data.comments;
            vue.pages = paging(page_total=vue.comments.page_total,
                            current_page=vue.comments.current_page);
        });
    }


    //提交comment
    function send_comment(reply_id, reply_user_id, reply_username, input_id){
        formValidate();
        if (!reply_id){
            reply_id = "";
            var reply_user_id = vue.post.user._id;
            var reply_username = vue.post.username;
        }else(
            $("#reply"+input_id).hide()
        );

        if (!input_id){
            input_id = "";
        }

        d = {
            content:$("#comment"+input_id).val(),
            target_id:vue.post._id,
            reply_id:reply_id,
            reply_user_id:reply_user_id,
            reply_username:reply_username
        }
        var result = osrHttp("POST","/api/comment", d);
        result.then(function (r) {
            vue.post.comment_num += 1;
            $("#comment"+input_id).val("");
            get_comment();
            if (input_id){
                togle_comment_input(input_id);
            }
        });
    }


     //点赞comment
    function ct_like(id, index){
        d = {
            id:id,
            type:"comment"
        }
        var result = osrHttp("PUT","/api/comment/like", d, args={not_prompt:true});
        result.then(function (r) {
            if (r.data.msg_type == "s"){
            if (vue.comments.datas[index].like_it_already){
                vue.comments.datas[index].like -= 1;
                vue.comments.datas[index].like_it_already = false;
            }else{
                vue.comments.datas[index].like += 1;
                vue.comments.datas[index].like_it_already = true;
            }
        }
        });
    }

    //回复已由评论的时候显示评论宽
    function togle_comment_input(id){
        var reply_div = $("#reply-"+id);
        if (reply_div.is(':hidden')){
            reply_div.show();
        }else{
            reply_div.hide();
        }
    }

    function ready_inform_ct(comment_obj){
        vue.ready_comment = comment_obj;
    }

