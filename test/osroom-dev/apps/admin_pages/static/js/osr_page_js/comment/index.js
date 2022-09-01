var vue = new Vue({
  el: '#app',
  delimiters:['{[', ']}'],
  data:{
      comments:{datas:{} },
      status:"is_issued",
      status_list:{
            '{{_("正常")}}':"is_issued",
            '{{_("未审核")}}':"not_audit",
            '{{_("未通过")}}':"unqualified",
            '{{_("待删除")}}':"user_remove"
           },
      keyword:"",
      checkAll:false,
      set:false,
      comment_view:{inform:{}},
      page:1,
      pages:{},
      sort:""
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
    var sort = $("#sort").attr("content");
    vue.sort = sort?sort:vue.sort;
    var keyword = $("#keyword").attr("content");
    vue.keyword = keyword?keyword:vue.keyword

    get_comments(vue.status,vue.page, vue.keyword);
})


function get_comments(status, page, keyword, sort_field){
    vue.keyword = keyword;
    vue.status = status;
    vue.page = page;

    var sort = sorting(sort_field);
    d = {
        page:page,
        status:vue.status,
        keyword:keyword,
        sort:JSON.stringify(sort)
    }

    var result = osrHttp("GET","/api/admin/comment",d,args={not_prompt:true});
    result.then(function (r) {
        vue.comments = r.data.comments;
        vue.checkAll = false;
        osr_check_all(vue.comments.datas, vue.checkAll, vue.set);
        vue.pages = paging(page_total=vue.comments.page_total,
                            current_page=vue.comments.current_page);
    });

    var url = window.location.pathname+"?page="+page+"&state="+vue.status+"&sort="+vue.sort;
    if(vue.keyword){
        url = url + "&keyword="+vue.keyword;
    }
    history_state(title=null,url=url);
}

function put_comment_view(index){
    vue.comment_view = vue.comments.datas[index];
}

function submit(){
    var operation = $("#operation option:selected").val();
    operation_comments(operation);
}

function operation_comments(operation){
    ids = JSON.stringify(osr_get_checked_id());
    if (operation=="approved"){
        var d = {
             op:"audit",
             ids:ids,
             score:0
             };
        // 提交数据
        var result = osrHttp("PUT","/api/admin/comment", d);
    }else if(operation=="non-approval"){
        var d = {
             op:"audit",
             ids:ids,
             score:100
             };
        // 提交数据
        var result = osrHttp("PUT","/api/admin/comment", d);

    }else if(operation=="pending_delete"){
        var d = {
             ids:ids,
             pending_delete:1
             };
        // 提交数据
        var result = osrHttp("DELETE","/api/admin/comment", d);

    }else if(operation=="delete"){
        var d = {
             ids:ids,
             pending_delete:0
             };
        // 提交数据
        var result = osrHttp("DELETE","/api/admin/comment", d);

    }else if(operation=="restore"){
        var d = {
             op:"restore",
             ids:ids,
             };
        // 提交数据
        var result = osrHttp("PUT","/api/admin/comment", d);

    }

    result.then(function (r) {
        if(r.data.msg_type=='s'){
            get_comments(vue.status, vue.page, vue.keyword);
        }
    });

}

function sorting(sort_field){
    // 反转排序
    if(sort_field=="issue_time"){
        if(vue.sort == "it-desc"){
            vue.sort = "it-asc";
        }else{
            vue.sort = "it-desc";
        }
    }else if(sort_field=="update_time"){
        if(vue.sort == "ut-desc"){
            vue.sort = "ut-asc";
        }else{
            vue.sort = "ut-desc";
        }
    }else if(sort_field=="like"){
        if(vue.sort == "like-desc"){
            vue.sort = "like-asc";
        }else{
            vue.sort = "like-desc";
        }
    }else if(sort_field=="pv"){
        if(vue.sort == "pv-desc"){
            vue.sort = "pv-asc";
        }else{
            vue.sort = "pv-desc";
        }
    }else if(sort_field=="comment_num"){
        if(vue.sort == "comment_num-desc"){
            vue.sort = "comment_num-asc";
        }else{
            vue.sort = "comment_num-desc";
        }
    }else if(sort_field=="word_num"){
        if(vue.sort == "word_num-desc"){
            vue.sort = "word_num-asc";
        }else{
            vue.sort = "word_num-desc";
        }
    }else if(sort_field=="audit_score"){
        if(vue.sort == "audit_score-desc"){
            vue.sort = "word_num-asc";
        }else{
            vue.sort = "audit_score-desc";
        }
    }else if(sort_field=="inform_total"){
        if(vue.sort == "inform_total-desc"){
            vue.sort = "inform_total-asc";
        }else{
            vue.sort = "inform_total-desc";
        }
    }

    //排序参数
    if(vue.sort=="it-desc"){
        sort = [{"issue_time":-1}];

    }else if(vue.sort=="it-asc"){
        sort = [{"issue_time":1}];

    }else if(vue.sort=="ut-desc"){
        sort = [{"update_time":-1}];

    }else if(vue.sort=="ut-asc"){
        sort = [{"update_time":1}];

    }else if(vue.sort=="like-desc"){
        sort = [{"like":-1}];

    }else if(vue.sort=="like-asc"){
        sort = [{"like":1}];

    }else if(vue.sort=="pv-desc"){
        sort = [{"pv":-1}];

    }else if(vue.sort=="pv-asc"){
        sort = [{"pv":1}];

    }else if(vue.sort=="comment_num-desc"){
        sort = [{"comment_num":-1}];

    }else if(vue.sort=="comment_num-asc"){
        sort = [{"comment_num":1}];

    }else if(vue.sort=="word_num-desc"){
        sort = [{"word_num":-1}];

    }else if(vue.sort=="word_num-asc"){
        sort = [{"word_num":1}];

    }else if(vue.sort=="audit_score-desc"){
        sort = [{"audit_score":-1}];

    }else if(vue.sort=="audit_score-asc"){
        sort = [{"audit_score":1}];

    }else if(vue.sort=="inform_total-desc"){
        sort = [{"inform.total":-1}];

    }else if(vue.sort=="inform_total-asc"){
        sort = [{"inform.total":1}];

    }else{
        sort = [{"issue_time": -1}, {"like": -1}, {"comment_num": -1}, {"pv": -1},];
    }

    return sort;
}
