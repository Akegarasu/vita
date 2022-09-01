
    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
          media_type:"text",
          medias:[],
          theme_name:"",
          page:1,
          media_view:{},
          media_edit:{},
          media_categorys:[],
          current_theme_name:null,
          theme_names:[],
          curren_category:"",
          checkAll:false, set:false,
          keyword:"",
          pages:{},
          page:1,
          sort:""
      },
      filters: {
            formatDate: function (time) {
              return formatDate(time, "yyyy-MM-dd hh:mm");
            }
      }
    })

    //加载完页面立即执行
    $(document).ready(function(){

        var cid = $("#cid").attr("content");
        vue.curren_category = cid;
        var url_s = get_url_parameter();
        vue.current_theme_name = get_obj_value(url_s, "theme", null);
        get_theme_names();
        var page = $("#page").attr("content");
        vue.page = page?page:vue.page;
        var sort = $("#sort").attr("content");
        vue.sort = sort?sort:vue.sort;
        var keyword = $("#keyword").attr("content");
        vue.keyword = keyword?keyword:vue.keyword;

    });

    //获取媒体数据
    function get_media(page, keyword, sort_field){
        vue.page = page;
        vue.keyword = keyword;

        var sort = sorting(sort_field);
        var d = {
            ctype:vue.media_type,
            theme_name: vue.current_theme_name,
            category_id:vue.curren_category,
            keyword:vue.keyword,
            page:vue.page,
            sort:JSON.stringify(sort)
        }

        var result = osrHttp("GET","/api/admin/theme/display-setting",d, args={not_prompt:true});
        result.then(function (r) {

            vue.medias = r.data.medias;
            vue.theme_name = r.data.theme_name;
            vue.checkAll = false;
            osr_check_all(vue.medias.datas, vue.checkAll, vue.set);
            vue.pages = paging(page_total=vue.medias.page_total,
             current_page=vue.medias.current_page);
        });
        var url = window.location.pathname+"?page="+page+"&cid="+vue.curren_category+"&sort="+vue.sort;
        if(vue.keyword){
            url = url + "&keyword="+vue.keyword;
        }
        if(vue.current_theme_name){
            url = url + "&theme="+vue.current_theme_name;
        }
        history_state(title=null,url=url);

    }

    //获取所有主题名称
    function get_theme_names(){

        var result = osrHttp("GET","/api/admin/theme-names",{},args={not_prompt:true});
        result.then(function (r) {
            vue.theme_names = r.data.names;
            vue.current_theme_name = vue.current_theme_name?vue.current_theme_name:r.data.current_theme_name;
            get_category();
        });
    }

    //获取分类
    function get_category(){

        var result = osrHttp(
            "GET","/api/admin/content/theme-category",
            {type:vue.media_type, theme_name:vue.current_theme_name},
            args={not_prompt:true});
        result.then(function (r) {
            vue.media_categorys = r.data.categorys;
            get_media(1, "");
        });
    }

    //全选
    function my_check_all(){
        osr_check_all(vue.medias.datas, vue.checkAll, vue.set);
        if(vue.checkAll){
            $("#check-btn-text").text("{{_('取消全选')}}");
        }else{
            $("#check-btn-text").text("{{_('全选')}}");
        }
        vue.checkAll = !vue.checkAll;

    }

    //切换要设置的主题
    function switch_theme_name(value) {
        vue.current_theme_name = value;
        get_category();
    }


    //切换分类
    function switch_category(value) {
        vue.curren_category = value.split("___")[0];
        get_media(1,'');
    }

    //删除媒体数据
    function del_media(){
        var ids = osr_get_checked_id();
        if(ids.length){
            ids = JSON.stringify(ids);
            var d = {
                theme_name: vue.current_theme_name,
                ids:ids
            }
            var result = osrHttp("DELETE","/api/admin/theme/display-setting", d);
            result.then(function (r) {
                if(r.data.msg_type="s"){
                    get_media();
                }
            });

        }else{
            alert_msg({msg:"请选择要删除的项", msg_type:"w"});
        }
    }

    function sorting(sort_field){
        // 反转排序
        if(sort_field=="time"){
            if(vue.sort == "time-desc"){
                vue.sort = "time-asc";
            }else{
                vue.sort = "time-desc";
            }
        }

        //排序参数
        if(vue.sort=="time-desc"){
            sort = [{"time":-1}];

        }else if(vue.sort=="time-asc"){
            sort = [{"time":1}];

        }
        return sort;
    }

