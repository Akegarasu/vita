
    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
            photos:[{}],
            category_names:[],
            current_category:[],
            sort:"t-desc",
            pages:[],
            page:1,
            img_w_h:"?w=0&h=120",
      },
      filters: {
            formatDate: function (time) {
              return irrformatDate(time, "yyyy-MM-dd hh:mm");
            }
      },
      updated:function(){
        //每次渲染完执行
        this.$nextTick(function(){
            if(this.current_category.length < 2){
                    var index = this.category_names.indexOf(this.current_category[0]);
                    nav_active("head_li_"+index);
                }else{
                    nav_active("head_li_all");
            }
        });
      }
    })

    // 加载完页面执行
    $(document).ready(function(){
        result = get_show_category();
        result.then(function (r) {

            var current_category = $("#category").attr("content");
            vue.current_category = current_category?current_category:"all";

            var url_s = get_url_parameter()
            vue.page = get_obj_value(url_s, "page", vue.page)

            if(!vue.current_category || vue.current_category == "all"){
                vue.current_category = vue.category_names;
            }else{
                vue.current_category = [vue.current_category]
            }
            get_global(vue.page, vue.current_category);


        });
    })

    function get_show_category(){

        var conditions = [
             {
                type:"text",
                names:["photo-page-nav"],
                result_key:"category_names"
             }

        ];
        var d ={
            conditions:JSON.stringify(conditions),
            theme_name:"osr-style"
        }

        var result = osrHttp("GET","/api/global/theme-data/display", d, args={not_prompt:true});
        result.then(function (r) {
            var category_names = r.data.medias.category_names.length===0?null:r.data.medias.category_names[0];
            if(category_names  && category_names.code_type=="html"){
                vue.category_names = JSON.parse(category_names.code);
            }else{
                 vue.category_names = category_names.code
            }
        });

        return result;
    }

    function get_global(page, category_name){
        vue.page = page;
        vue.current_category = category_name;
        var d ={
            category_type:"image",
            category_name:JSON.stringify(vue.current_category),
            page:vue.page,
            pre:12
        }

        var result = osrHttp("GET","/api/global/media", d, args={not_prompt:true});

        result.then(function (r) {
            vue.photos = r.data.medias;
            vue.pages = paging(page_total=vue.photos.page_total, current_page=vue.photos.current_page);
        });

        if(vue.current_category.length < 2){
            var temp_category = vue.current_category[0];
        }else{
            var temp_category = "all";
        }

        var url = window.location.pathname
                    +"?category="+temp_category
                    +"&page="+page
        history_state(null, url);
    }

    //初始化图片查看器
    var is_init_viewer = false;
    function init_viewer(id) {
        id = id?id:"galley";
        if(!is_init_viewer){
            var $images = $('#'+id);
            $images.on({}).viewer({
                interval:2500
            });
            is_init_viewer = true;
        }
        $('#'+id).on({}).viewer('update');
    }


