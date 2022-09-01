
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
            posts:{datas:[]},
            sort:"t-desc",
            tag:"",
            pages:[],
            page:1,
            img_w_h:"?w=0&h=120",
            is_myself:null
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
        vue.category_id = get_obj_value(url_s, "id")
        vue.sort = get_obj_value(url_s, "sort", vue.sort)
        vue.page = get_obj_value(url_s, "page", vue.page)
        vue.tag = get_obj_value(url_s, "tag", "")
        document.title = vue.tag + "-" + "{{g.site_global.site_config.TITLE_SUFFIX}}";
        nav_active("head_li_sort_"+vue.sort);

        // get post
        get_posts(vue.page, vue.sort);

    });


    //获取
    function get_posts(page, sort){

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
            pre:10,
            status:"is_issued",
            sort:JSON.stringify(sort),
            unwanted_fields:JSON.stringify(["content", "imgs"])
        }

        var result = osrHttp("GET","/api/post", d, args={not_prompt:true});
        result.then(function (r) {
            $.each(r.data.posts.datas, function(index, value) {
                if(value.editor=="markdown"){
                    r.data.posts.datas[index]["brief_content"] = marked(value.brief_content);
                }
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
        });

    }


