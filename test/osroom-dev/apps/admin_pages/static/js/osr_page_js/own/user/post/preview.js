

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
            comments:{},
            sort:'t-desc',
            page:1,
            pages:[],
            ready_comment:{} //准备举报的评论
      },
      filters: {
            formatDate: function (time) {
              return irrformatDate(time, "yyyy-MM-dd hh:mm");
            }
      }
    })

    vue.post_id = $("#post_id").attr("content");
    // 加载完页面执行
    $(document).ready(function(){
        get_post();
        get_comment(vue.sort, vue.page);
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


