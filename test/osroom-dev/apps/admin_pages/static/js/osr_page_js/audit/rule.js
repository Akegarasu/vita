var vue = new Vue({
  el: '#app',
  delimiters:['{[', ']}'],
  data:{
    keys:{},
    page:1,
    keyword:"",
    project:null,
    project_info:"",
    audit_rules:[],
    new_rule:"",
    checkAll:false,
    set:false,
    pages:{}
  },
  methods: {show_btn:show_btn},
  filters: {
        formatKey: function (key) {
          return formatStr(key);
        }
  }
})

// 加载完页面执行
$(document).ready(function(){

    var result = osrHttp("GET","/api/admin/audit/rule/key", {}, args={not_prompt:true});
    result.then(function (r) {
        vue.keys = r.data.keys;
        $.each(vue.keys, function(index, value){
            vue.project = index;
            return false;
        });

        var project = $("#project").attr("content");
        vue.project = project?project:vue.project;
        var page = $("#page").attr("content");
        vue.page = page?page:vue.page;
        var keyword = $("#keyword").attr("content");
        vue.keyword = keyword?keyword:vue.keyword;

        get_audit_rules(vue.project, vue.page, vue.keyword);

    });
});

function show_btn(id){
    if( $("#"+id).hasClass("show") ){
        // 执行隐藏
        $("#"+id).hide().removeClass("show");
        // 其他
    }else{
        // 显示
        $("#"+id).show().addClass("show");
    }
}
function get_audit_rules(project, page, keyword){
    vue.project = project;
    vue.keyword = keyword;
    vue.page = page;
    vue.project_info = vue.keys[project];
    var d = {
        project:vue.project,
        page:page,
        keyword:keyword
    }

    var result = osrHttp("GET","/api/admin/audit/rule", d, args={not_prompt:true});
    result.then(function (r) {
        vue.audit_rules = r.data.rules;
        vue.checkAll = false;
        osr_check_all(vue.audit_rules.datas, vue.checkAll, vue.set);
        vue.pages = paging(page_total=vue.audit_rules.page_total,
                            current_page=vue.audit_rules.current_page);
    });

    var url = window.location.pathname+"?page="+page+"&project="+vue.project;
    if(vue.keyword){
        url = url + "&keyword="+vue.keyword;
    }
    history_state(title=null,url=url);
}

function add(){
    formValidate();
    var d = {
        project:vue.project,
        rule:vue.new_rule
    }
    // 提交数据
    var result = osrHttp("POST","/api/admin/audit/rule", d);
    result.then(function (r) {
        if (r.data.msg_type=="s"){
            get_audit_rules(vue.project, 1, "");
            vue.new_rule = "";
        }
    });
}


function del(ids){
    if(!ids){
        ids = osr_get_checked_id();
    }
    var d = {
        ids:JSON.stringify(ids)
    }
    // 提交数据
    var result = osrHttp("DELETE","/api/admin/audit/rule", d);
    result.then(function (r) {
        if (r.data.msg_type=="s"){
            get_audit_rules(vue.project, vue.page, "");
        }
    });
}