
    Vue.directive('highlight',function (el) {
      let blocks = el.querySelectorAll('pre code');
      blocks.forEach((block)=>{
        hljs.highlightBlock(block)
      })
    })

    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
            user:{profile:{}, avatar_url:{}, follow:{}},
            status:"is_issued",
            posts:{datas:[]},
            is_myself:null,
            sort:"t-desc",
            keyword:"",
            user_id:null,
            pages:[],
            page:1,
            img_w_h:"?w=0&h=120",
            post_categorys:[]
      },
      filters: {
            formatDate: function (time) {
              return irrformatDate(time, "yyyy-MM-dd hh:mm");
            }
      }

    })


    // 加载完页面执行
    $(document).ready(function(){

        {% if current_user.is_authenticated %}
            var current_user_id = "{{current_user.id}}";
        {% else %}
            var current_user_id = null;
        {% endif %}

        var url_s = get_url_parameter()
        vue.status = get_obj_value(url_s, "state", vue.status)
        vue.user_id = get_obj_value(url_s, "id", current_user_id)
        vue.sort = get_obj_value(url_s, "sort", vue.sort)
        vue.page = get_obj_value(url_s, "page", vue.page)

        if(vue.user_id == current_user_id){
            vue.is_myself = true;
        }
        if(vue.status == "is_issued"){
            nav_active("head_li_sort_"+vue.sort);
        }else{
            nav_active("head_li_status_"+vue.status);
        }

        // get post
        get_posts(vue.status, vue.page, vue.sort, vue.keyword);
        get_user();

    });


    function get_user(){
        d = {
            user_id:vue.user_id,
            is_basic:0
        }

        var result = osrHttp("GET","/api/account/profile/public", d, args={not_prompt:true});
        result.then(function (r) {
            vue.user = r.data.user;
            get_post_categorys();
            document.title = vue.user.username + "-" + "{{g.site_global.site_config.TITLE_SUFFIX}}";
        });
    }

    function get_post_categorys(){
        d = {
            action:"get_category",
            type:"post",
            user_id:vue.user._id
        }

        var result = osrHttp("GET","/api/content/user/post/category", d, args={not_prompt:true});
        result.then(function (r) {
            vue.post_categorys = r.data.categorys;
        });
    }

    //获取
    function get_posts(status, page, sort, keyword){

        vue.keyword = keyword;
        vue.status = status;
        vue.sort = sort;
        vue.page = page;
        if(!sort || vue.status=="draft" || vue.status=="recycle"){
            vue.sort = "t-desc";
        }else{
            vue.sort = sort;
        }

        if(sort=="t-desc"){
            if(vue.status=="draft"){
                sort = [{"update_time":-1}, {"issue_time":-1}];
            }else{
                sort = [{"issue_time":-1},{"update_time":-1}];
            }

        }else if(sort=="t-asc"){
            if(vue.status=="draft"){
                sort = [{"update_time":1}, {"issue_time":1}];
            }else{
                sort = [{"issue_time":1},{"update_time":1}];
            }

        }else{
            sort = [{"like": -1}, {"comment_num": -1}, {"pv": -1},{"issue_time": -1}];
        }

        d = {
            page:page,
            pre:15,
            status:vue.status,
            keyword:vue.keyword,
            sort:vue.sort,
            user_id:vue.user_id,
            sort:JSON.stringify(sort),
            unwanted_fields:JSON.stringify(["content", "imgs"])
        }

        var result = osrHttp("GET","/api/post", d, args={not_prompt:true});
        result.then(function (r) {
            vue.posts = r.data.posts;
            $.each(vue.posts.datas, function(index, value) {
                if(value.editor=="markdown"){
                    vue.posts.datas[index]["brief_content"] = marked(value.brief_content);
                }
            });
            vue.pages = paging(page_total=vue.posts.page_total,
            current_page=vue.posts.current_page);
        });

        var url = window.location.pathname
                    +"?id="+vue.user_id
                    +"&sort="+vue.sort
                    +"&page="+page
                    +"&state="+vue.status;
        if(vue.keyword){
            url = url+'&keyword='+vue.keyword;
        }
        history_state(null, url);
    }

    //删除
    function del_posts(id, recycle){
        if (recycle){
            recycle = 1;
        }else{
            recycle = 0;

        }
        d = {
            ids:JSON.stringify([id]),
            recycle:recycle
        }
        var result = osrHttp("DELETE","/api/user/post",d);
        result.then(function (r) {
            if(r.data.msg_type=='s'){
                get_posts(vue.status, 1, vue.sort, vue.keyword)
            }
        });
    }

    //恢复
    function restore_posts(id){

        d = {
            op:"restore",
            ids:JSON.stringify([id])
        }

        var result = osrHttp("PUT","/api/user/post",d);
        result.then(function (r) {
            if(r.data.msg_type=='s'){
                get_posts(vue.status, 1, vue.sort, vue.keyword)
            }
        });
    }

    //添加关注
    function follow(id){

        d = {
            ids:JSON.stringify([id])
        }
        var result = osrHttp("POST","/api/user/follow",d);
        result.then(function (r) {
            if(r.data.msg_type=='s'){
                get_user();
            }
        });
    }



    function unfollowed(id){

        d = {
            ids:JSON.stringify([id])
        }
        var result = osrHttp("DELETE","/api/user/follow",d);
        result.then(function (r) {
            if(r.data.msg_type=='s'){
                get_user();
            }
        });
    }

