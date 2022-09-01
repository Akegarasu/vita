
    // Vue.directive('highlight',function (el) {
    //   let blocks = el.querySelectorAll('pre code');
    //   blocks.forEach((block)=>{
    //     hljs.highlightBlock(block)
    //   })
    // })

    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
            posts:{datas:[]},
            sort:"t-desc",
            tag:"",
            pages:{current_page:1},
            page:1,
            img_w_h:"?w=0&h=120",
            is_myself:null,
            single:false,
            tags:[],
            tag_index:0
      },
      filters: {
            formatDate: function (time) {
              return irrformatDate(time, "yyyy-MM-dd hh:mm");
            }
      },
      updated:function(){
        //每次渲染完执行
        this.$nextTick(function(){
             nav_btn_active("tag-nav", "tag_"+vue.tag_index);
        });
      }

    })

    // 加载完页面执行
    $(document).ready(function(){
        vue.colors = osr_colors();
        var url_s = get_url_parameter()
        vue.category_id = get_obj_value(url_s, "id")
        vue.single = get_obj_value(url_s, "single", vue.single)
        vue.sort = get_obj_value(url_s, "sort", vue.sort)
        vue.page = get_obj_value(url_s, "page", vue.page)
        vue.tag = get_obj_value(url_s, "tag", null)
        result = get_post_tags();

        result.then(function (r) {
            // get post
            get_posts(vue.page, vue.sort);
        });

    });

    function switch_tag(tag, index){
        vue.tag = tag;
        get_posts(1, vue.sort);
        vue.tag_index = index;
    }

    function get_post_tags(){
        var d ={
            limit:30,
            last_days:360
        }

        var result = osrHttp("GET","/api/post/tags", d, args={not_prompt:true});
        result.then(function (r) {
            vue.tags = r.data.tags;
            for(var i in vue.tags){
                if (vue.tags[i]["tag"] == vue.tag){
                    vue.tag_index = i;
                    break;
                }
            }
            if(!vue.tag && vue.tags.length){
                vue.tag = vue.tags[0]["tag"];
            }
        });
        return result;
    }

    //获取
    function get_posts(page, sort){

        if (!vue.tag){
            return;
        }
        vue.sort = sort;
        vue.page = page;
        if(sort=="t-desc"){
            sort = [{"issue_time":-1},{"update_time":-1}];
        }else if(sort=="t-asc"){
           sort = [{"issue_time":1},{"update_time":1}];
        }else{
            sort = [{"like": -1}, {"comment_num": -1}, {"pv": -1},{"issue_time": -1}];
        }

        d = {
            page:page,
            tag:vue.tag,
            pre:12,
            status:"is_issued",
            sort:JSON.stringify(sort),
            unwanted_fields:JSON.stringify(["content", "imgs"])
        }

        var result = osrHttp("GET","/api/post", d, args={not_prompt:true});
        result.then(function (r) {
            $.each(r.data.posts.datas, function(index, value) {
                if(value["tags"].length>3 && value.brief_content.length>25){
                    value.brief_content = value.brief_content.slice(0, 25)
                }
                // if(value.editor=="markdown"){
                //     r.data.posts.datas[index]["brief_content"] = marked(value.brief_content);
                // }
            });
            vue.pages = paging(page_total=r.data.posts.page_total, current_page=r.data.posts.current_page);
            if(vue.page!=1){
                var old_datas = vue.posts.datas;
                vue.posts = r.data.posts;
                $.merge(old_datas, r.data.posts.datas);
                vue.posts.datas = old_datas;
            }else{
                vue.posts = r.data.posts;
            }
            document.title = vue.tag + "-" + "{{g.site_global.site_config.TITLE_SUFFIX}}";
            nav_active("head_li_sort_" + vue.sort);
            var url = window.location.pathname
                    +"?tag="+vue.tag
                    +"&sort="+vue.sort
                    +"&page="+page
                    +"&single="+single
            history_state(null, url);

        });

    }


