
    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
            type:"all",
            files:[],
            keyword:"",
            search_cnt:0,
            del_filename:"",
            del_file_path:"",
            confirm_filename:"",
            theme_names: [],
            current_theme_name: null,
            page:1,
            pages:{},
            type_list:{
                '{{_("所有文件")}}':"all",
                '{{_("自带文件")}}':"default",
                '{{_("自定义文件")}}':"custom"
               },
            }
    })

    // 加载完页面执行
    $(document).ready(function(){

        var type = $("#type").attr("content");
        vue.type = type?type:vue.type;
        var page = $("#page").attr("content");
        vue.page = page?page:vue.page;
        var keyword = $("#keyword").attr("content");
        vue.keyword = keyword?keyword:vue.keyword;
        var url_s = get_url_parameter();
        vue.current_theme_name = get_obj_value(url_s, "theme", null);
        get_theme_names();

    })

    //获取所有主题名称
    function get_theme_names(){
        var result = osrHttp("GET","/api/admin/theme-names",{},args={not_prompt:true});
        result.then(function (r) {
            vue.theme_names = r.data.names;
            vue.current_theme_name = vue.current_theme_name?vue.current_theme_name:r.data.current_theme_name;
            get_files(vue.page, "");
        });
    }

    //切换要设置的主题
    function switch_theme_name(value) {
        vue.current_theme_name = value;
        get_files(1, "");
    }

    function switch_type(value){
        vue.type = value;
        get_files(1, "");
    }
    function get_files(page, keyword){
        vue.page = page;
        vue.keyword = keyword;
        d = {
            keyword:keyword,
            theme_name: vue.current_theme_name,
            page:page,
            pre:10,
            type:vue.type
        }

       var result = osrHttp("GET","/api/admin/static/file", d, args={not_prompt:true});
       result.then(function (r) {
            vue.files = r.data.files;
            if(vue.keyword){
                vue.search_cnt = 1;
            }
            vue.pages = paging(page_total=vue.files.page_total,
                                current_page=vue.files.current_page);

       });

        var url = window.location.pathname+"?type="+vue.type+"&page="+page;
        if(vue.keyword){
            url = url + "&keyword="+vue.keyword;
        }
        if(vue.current_theme_name){
            url = url + "&theme="+vue.current_theme_name;
        }
        history_state(title=null,url=url);
    }

    function del_file(path, filename){
        d = {
            file_path:path,
            filename:filename,
            theme_name: vue.current_theme_name,
        }
        if(vue.confirm_filename == vue.del_filename){
             var result = osrHttp("DELETE","/api/admin/theme/page", d);
             result.then(function (r) {
                if(r.data.msg_type=="s"){
                    get_files(vue.page, "");
                }
             });

        }else{
            alert("确认失败!");
        }

    }

