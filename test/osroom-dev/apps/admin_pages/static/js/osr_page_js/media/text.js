
    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
          media_type:"text",
          medias:[],
          page:1,
          media_view:{},
          media_edit:{},
          media_categorys:[],
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
        get_category();
        var page = $("#page").attr("content");
        vue.page = page?page:vue.page;
        var sort = $("#sort").attr("content");
        vue.sort = sort?sort:vue.sort;
        var keyword = $("#keyword").attr("content");
        vue.keyword = keyword?keyword:vue.keyword;

        get_media(vue.page, vue.keyword)
    });

    //获取媒体数据
    function get_media(page, keyword, sort_field){
        vue.page = page;
        vue.keyword = keyword;

        var sort = sorting(sort_field);
        var d = {
            ctype:vue.media_type,
            category_id:vue.curren_category,
            keyword:vue.keyword,
            page:vue.page,
            sort:JSON.stringify(sort)
        }

        var result = osrHttp("GET","/api/admin/upload/media-file",d,args={not_prompt:true});
        result.then(function (r) {

            vue.medias = r.data.medias;
            vue.checkAll = false;
            osr_check_all(vue.medias.datas, vue.checkAll, vue.set);
            vue.pages = paging(page_total=vue.medias.page_total,
             current_page=vue.medias.current_page);
        });
        var url = window.location.pathname+"?page="+page+"&cid="+vue.curren_category+"&sort="+vue.sort;
        if(vue.keyword){
            url = url + "&keyword="+vue.keyword;
        }
        history_state(title=null,url=url);

    }

    //获取分类
    function get_category(){

        var result = osrHttp("GET","/api/admin/content/category",{type:vue.media_type},args={not_prompt:true});
        result.then(function (r) {
            vue.media_categorys = r.data.categorys;
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
                ids:ids
            }
            var result = osrHttp("DELETE","/api/admin/upload/media-file", d);
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

