
    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
            user_id:null,
            user:{profile:{}, avatar_url:{}, follow:{}},
            user_related_users:{},
            fans:{},
            keyword:"",
            pages:[],
            page:1,
            type:"followed_user",
            is_myself:0
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

        vue.type = get_obj_value(url_s, "t", vue.type)
        vue.user_id = get_obj_value(url_s, "id", current_user_id)
        vue.page = get_obj_value(url_s, "page", vue.page)
        vue.keyword = get_obj_value(url_s, "keyword", vue.keyword)

        if(vue.user_id == current_user_id){
            vue.is_myself = true;
        }
        if(vue.status == "is_issued"){
            nav_active("head_li_"+vue.type);
        }else{
            nav_active("head_li_"+vue.type);
        }

        get_user();
        get_related_users(vue.type, vue.page, vue.keyword);

    });

    //获取当前页面用户的基础资料
    function get_user(){
        d = {
            user_id:vue.user_id,
            is_basic:0
        }
        var result = osrHttp("GET","/api/account/profile/public", d, args={not_prompt:true});
        result.then(function (r) {
            vue.user = r.data.user;
            document.title = vue.user.username + "-" + "{{g.site_global.site_config.TITLE_SUFFIX}}";
        });
    }
    //获取已关注的
    function get_related_users(type, page, keyword){
        vue.type = type?type:vue.type;
        vue.page = page?page:vue.page;
        vue.keyword = keyword?keyword:vue.keyword;
        d = {
            user_id:vue.user_id,
            action:type,
            pre:20,
            page:page
        }

        var result = osrHttp("GET","/api/user/follow", d, args={not_prompt:true});
        result.then(function (r) {
            vue.user_related_users = r.data.users;
            vue.pages = paging(page_total=vue.user_related_users.page_total,
                        current_page=vue.user_related_users.current_page);
        });

        var url = window.location.pathname
                    +"?t="+vue.type
                    +"&id="+vue.user_id
                    +"&page="+vue.page;
        if(vue.keyword){
            url = url+'&keyword='+vue.keyword;
        }
        history_state(null, url);
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
                get_related_users(vue.type, vue.page, vue.keyword);
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
                get_related_users(vue.type, vue.page, vue.keyword);
            }
        });
    }

