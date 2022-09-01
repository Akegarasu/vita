

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
            post_id:"",
            post:{user:{avatar_url:{}, follow:{}}},
            inform:{},
            sort:'like',
            rec_1:[],
            comments:{},
            page:1,
            pages:[],
            ready_comment:{}, //准备举报的评论,
            loged_user:null,
            vst_username:"",
            vst_email:""
      },
      filters: {
            formatDate: function (time) {
              return irrformatDate(time, "yyyy-MM-dd hh:mm");
            }
      }
    })


    // 加载完页面执行
    $(document).ready(function(){
        var url_s = get_url_parameter()
        vue.post_id = get_obj_value(url_s, "id")
        get_post();
        get_comment();
        get_rec();

        {% if current_user.is_authenticated %}
            vue.loged_user = "{{current_user.id}}";
        {% endif %}

    })

    function get_post(){

        d = {
            post_id:vue.post_id,
        }

        var result = osrHttp("GET","/api/post", d, args={not_prompt:true});
        result.then(function (r) {
            vue.post = r.data.post;
            if(vue.post.editor=="markdown"){
                vue.post.content = marked(vue.post.content);
            }

            history_state(vue.post.title+"-{{g.site_global.site_config.TITLE_SUFFIX}}");
        }).catch(function (r){
            alert_msg({msg:"{{_('当前访问的内容已不存在')}}", msg_type:"e"})
        });
    }

    //喜欢post
    function like(){
        d = {
            id:vue.post._id,
            action:"like"
        }

        var result = osrHttp("PUT","/api/post",d, {not_prompt:true});
        result.then(function (r) {
            if (r.data.msg_type == "s"){
                if (vue.post.like_it_already){
                    vue.post.like -= 1;
                    vue.post.like_it_already = false;
                }else{
                    vue.post.like += 1;
                    vue.post.like_it_already = true;
                }
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
                vue.post.user.follow.current_following = !vue.post.user.follow.current_following;
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
                vue.post.user.follow.current_following = !vue.post.user.follow.current_following;
            }
        });
    }

    function get_rec(){
        var conditions = [
             {
                type:"image",
                name_regex:"post-rec1-*[0-9]*",
                result_key:"rec_1"
             },

        ];
        var d ={
            conditions:JSON.stringify(conditions),
            theme_name:"osr-theme-w"
        }
        var result = osrHttp("GET","/api/global/theme-data/display", d, args={not_prompt:true});
        result.then(function (r) {
            vue.rec_1 = r.data.medias.rec_1!=[]?r.data.medias.rec_1[0]:[];

        });
    }

