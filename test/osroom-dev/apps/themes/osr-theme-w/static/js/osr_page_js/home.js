var vue = new Vue({
  el: '#app',
  delimiters:['{[', ']}'],
  data:{
        carousel:[{}],
        home_display:null,
        home_display_img: null,
        home_display_cover: null,
        display_tag:0,
        posts:{datas:[]},
        sort:"t-desc",
        pages:[],
        page:1,
        tags:{},
        img_w_h:"?w=0&h=120",
        colors:[]
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
         {
            type:"text",
            name_regex:"home-display-[0-9]+",
            result_key:"home_display"
         },
        {
            type:"text",
            name_regex:"display_tag",
            result_key:"display_tag"
         },
        {
            type:"image",
            name_regex:"home-display-img-[0-9]+",
            result_key:"home_display_img"
         },
        {
            type:"image",
            name_regex:"home-display-cover-[0-9]+",
            result_key:"home_display_cover"
         }
    ];
    var d ={
        conditions:JSON.stringify(conditions),
        theme_name:"osr-theme-w"
    }
    var result = osrHttp("GET","/api/global/theme-data/display", d, args={not_prompt:true});
    result.then(function (r) {
        vue.display_tag =  r.data.medias.display_tag.length===0?null:r.data.medias.display_tag[0];
        vue.home_display = r.data.medias.home_display;
        vue.home_display = vue.home_display.length === 0?null:vue.home_display;
        vue.home_display_img = r.data.medias.home_display_img;
        vue.home_display_img = vue.home_display_img.length === 0?null:vue.home_display_img;

        vue.home_display_cover = r.data.medias.home_display_cover.length === 0?null:r.data.medias.home_display_cover[0];
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
        pre:6,
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
    });
}

function get_post_tags(){
    var d ={
        limit:30,
        last_days:360
    }

    var result = osrHttp("GET","/api/post/tags", d, args={not_prompt:true});
    result.then(function (r) {
        vue.tags = r.data.tags;
    });
    }