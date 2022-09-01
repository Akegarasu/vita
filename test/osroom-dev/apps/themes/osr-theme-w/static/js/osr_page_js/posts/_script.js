
var vue = new Vue({
    el: '#app',
    delimiters:['{[', ']}'],
    data:{
            carousel:[{}],
            rec_1:[{}],
            rec_2:[],
            rec_3:[{}],
            rec_4:[{}],
            posts:{datas:[]},
            sort:"t-desc",
            pages:[],
            page:1,
            tags:{},
            img_w_h:"?w=0&h=120",
            color:[],
        display_tag:null
    },
    filters: {
            formatDate: function (time) {
            return irrformatDate(time, "yyyy-MM-dd hh:mm");
            }
    }
    })

    // 加载完页面执行
    $(document).ready(function(){
        vue.colors = osr_colors();
        get_global();
        get_posts(vue.page, vue.sort);
        get_post_tags();
    })

    function get_global(){
        var conditions = [
        ];
        var d ={
            conditions:JSON.stringify(conditions),
            theme_name:"osr-theme-w"
        }

        var result = osrHttp("GET","/api/global/theme-data/display", d, args={not_prompt:true});
        result.then(function (r) {
            vue.display_tag =  r.data.medias.display_tag.length===0?null:r.data.medias.display_tag[0];
            vue.carousel = r.data.medias.home_carousel;
            vue.rec_1 = r.data.medias.rec_1;
            vue.rec_2 = r.data.medias.rec_2!=[]?r.data.medias.rec_2[0]:[];
            vue.rec_3 = r.data.medias.rec_3;
            vue.rec_4 = r.data.medias.rec_4;
        });
    }

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

    function get_post_tags(){
        var d ={
            limit:20,
            last_days:360
        }

        var result = osrHttp("GET","/api/post/tags", d, args={not_prompt:true});
        result.then(function (r) {
            vue.tags = r.data.tags;
        });


    }

