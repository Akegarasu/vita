
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
            category_id:null,
            category:{name:'{{_("全部文章")}}'},
            user:{profile:{}, avatar_url:{}, follow:{}},
            posts:{datas:[]},
            sort:"t-desc",
            pages:[],
            page:1,
            status:"is_issued",
            img_w_h:"?w=0&h=120",
            is_myself:false,
            post_categorys:[],
            user_id:null,
          colors:[]
      },
      filters: {
            formatDate: function (time) {
              return irrformatDate(time, "yyyy-MM-dd hh:mm");
            }
      },
      updated:function(){
        //每次渲染完执行
        this.$nextTick(function(){
            nav_btn_active("post-category", "cid"+vue.category_id);
        });
      }

    })

    // 加载完页面执行
    $(document).ready(function(){
        vue.colors =  osr_colors();
        nav_btn_active("post-category", "cidnull");
        var url_s = get_url_parameter();
        var cid = get_obj_value(url_s, "cid");
        vue.category_id = cid?cid:null;
        vue.user_id = get_obj_value(url_s, "id");
        vue.user_id = vue.user_id?vue.user_id:'{{current_user.id}}';
        vue.sort = get_obj_value(url_s, "sort", vue.sort);
        //vue.status = get_obj_value(url_s, "state", vue.status)
        vue.page = get_obj_value(url_s, "page", vue.page);
        nav_active("head_li_sort_"+vue.sort);

        // 获取category
        result = get_category_info();
        if(!vue.user_id && result){
             result.then(function (r) {
                //获取用户资料
                get_user();
                document.title = vue.category.name + "-" + "{{g.site_global.site_config.TITLE_SUFFIX}}";
            });
        }else{
            //获取用户资料
            get_user();
            document.title = vue.category.name + "-" + "{{g.site_global.site_config.TITLE_SUFFIX}}";
        }
        // get post
        get_posts(vue.page, vue.sort);

    });

    function get_category_info(){
        if(vue.category_id && vue.category_id != 'null'){
            d = {
                id:vue.category_id
            }
             var result = osrHttp("GET","/api/content/category/info",d,args={not_prompt:true});
            result.then(function (r) {
                vue.category = r.data.category;
                vue.user_id = vue.category.user_id;
            });
            return result;
        }
    }
    function get_user(){
        d = {
            user_id:vue.user_id,
            is_basic:0
        }
        var result = osrHttp("GET","/api/account/profile/public", d, args={not_prompt:true});
        result.then(function (r) {
            vue.user = r.data.user;
            //获取当前登录用户id
            {% if current_user.is_authenticated %}
                var current_user_id = "{{current_user.id}}";
            {% else %}
                var current_user_id = false;
            {% endif %}
            if(vue.user._id == current_user_id){
                vue.is_myself = true;
            }

            get_post_categorys();
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

    function switch_category(category) {
        vue.category_id = category?category._id:null;
        vue.category = category?category:{name:'{{_("全部文章")}}'};
        if (vue.category.name == ""){
            vue.category.name='{{_("默认文集")}}';
        }

        get_posts(1, vue.sort);
    }

    function switch_state(status, sort) {
        vue.status = status;
        vue.sort = sort;
        get_posts(1, vue.sort);
    }

    //获取
    function get_posts(page, sort){
        vue.sort = sort;
        vue.page = page;
        if(!sort || vue.status=="draft" || vue.status=="recycle"){
            vue.sort = "t-desc";
        }else{
            vue.sort = sort;
        }

        if(sort=="t-desc"){
            sort = [{"issue_time":-1},{"update_time":-1}];
        }else if(sort=="t-asc"){
            sort = [{"issue_time":1},{"update_time":1}];
        }else{
            sort = [{"like": -1}, {"comment_num": -1}, {"pv": -1},{"issue_time": -1}];
        }

        d = {
            page:vue.page,
            pre:12,
            status:vue.status,
            sort:JSON.stringify(sort),
            user_id:vue.user_id,
            unwanted_fields:JSON.stringify(["content", "imgs"])
        }
        if (vue.category_id && vue.category_id!='null' && vue.category_id!=''){
            d["category_id"] = vue.category_id
        }
        var result = osrHttp("GET","/api/post", d, args={not_prompt:true});
        result.then(function (r) {
            vue.posts = r.data.posts;
            $.each(vue.posts.datas, function(index, value) {
                 if(value["tags"].length>3 && value.brief_content.length>25){
                    value.brief_content = value.brief_content.slice(0, 25)
                }
                // if(value.editor=="markdown"){
                //     vue.posts.datas[index]["brief_content"] = marked(value.brief_content);
                // }
            });

            vue.pages = paging(page_total=vue.posts.page_total,
                        current_page=vue.posts.current_page);
        });
        var url = window.location.pathname
                    +"?id="+vue.user_id
                    +"&cid="+vue.category_id
                    +"&sort="+vue.sort
                    +"&page="+page
        history_state(null, url);
        document.title = vue.category.name + "-" + "{{g.site_global.site_config.TITLE_SUFFIX}}";

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

        var result = osrHttp("DELETE", "/api/user/post",d);
        result.then(function (r) {
             if(r.data.msg_type=='s'){
                get_posts(1, vue.sort)
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
                get_posts(1, vue.sort)
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

