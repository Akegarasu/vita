
    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
        media:{title:"",
               name:"",
               type:"",
               link:"",
               link_name:"",
               text:"",
               text_html:"",
               category_id:"",
               link_open_new_tab:1,
               code:"",
               code_type:"html"
        },
        current_theme_name:null,
        new_category_id:null,
        media_categorys:[{}],
        id:null,
        cid:"",
        img_w_h:"?w=0&h=140"
      }
    })

    // 加载完页面执行
    $(document).ready(function(){
        var id = $("#id").attr("content")
        vue.media.type = media_type;
        vue.media.category_id = $("#cid").attr("content")
        var url_s = get_url_parameter();
        vue.current_theme_name = get_obj_value(url_s, "theme");
        if(vue.cid=="null" || vue.cid == "undefined" || vue.cid == undefined){
            vue.cid = ""
        }
        if(id!="null" && id != "undefined" && id != undefined && id){
            vue.id = id;
            get_media();
        }else{
            //只获取分类
            get_category();
        }
    });

    //获取分类
    function get_category(){

        var result = osrHttp("GET","/api/admin/content/theme-category",
            {type:vue.media.type, theme_name:vue.current_theme_name},
            args={not_prompt:true});
        result.then(function (r) {
            vue.media_categorys = r.data.categorys;
        });
    }

    //获取
    function get_media(){
        var d = {
            theme_name: vue.current_theme_name,
            id:vue.id
        }

        var result = osrHttp("GET","/api/admin/theme/display-setting",d,args={not_prompt:true});
        result.then(function (r) {
            vue.media = r.data.media;
            if (vue.media.code_type == "json") {
                vue.media.code = JSON.stringify(vue.media.code);
            }
            editor.txt.html(vue.media.text_html);
            get_category();
        });
    }

    function switch_category(value){
        vue.new_category_id = value;
    }

    //保存
    function save(){
        formValidate();
        vue.media.text = editor.txt.text();
        vue.media.html = editor.txt.html();
        var d = {
             theme_name: vue.current_theme_name,
             name:vue.media.name,
             title:vue.media.title,
             ctype:vue.media.type,
             link:vue.media.link,
             link_open_new_tab:vue.media.link_open_new_tab,
             link_name:vue.media.link_name,
             text:vue.media.text,
             text_html:vue.media.html,
             code:vue.media.code,
             code_type:vue.media.code_type
        }
        if(vue.new_category_id){
            d["category_id"] = vue.new_category_id;
            vue.new_category_id = null;
        }
         if(vue.media.switch == 1 || vue.media.switch == 0){
            d["switch"] = vue.media.switch;
        }

        // 提交数据
        if(vue.id){
            //更新
            d["id"] = vue.id
            var result = osrHttp("PUT","/api/admin/theme/display-setting", d);
            result.then(function (r) {
                if(r.data.msg_type=="s"){
                     //window.location.href='/osr-admin/theme-setting/display/'+vue.media.type+'-edit?cid='+vue.cid
                     //+'&id='+vue.id;
                     location.reload();
                }
            });

        }else{
            //添加
            var result = osrHttp("POST","/api/admin/theme/display-setting", d);
            result.then(function (r) {
                if(r.data.msg_type == "s"){
                    //window.location.href='/osr-admin/theme-setting/display/'+vue.media.type+'?cid='+vue.cid;
                    location.reload();
                }
            });
        }


    }

    function upload_img(){

        var formData = new FormData();
        var name = $("#upfile").attr("name");
        var paths = $("#upfile")[0].files;
        for(var j = 0,len=paths.length; j < len; j++) {
            formData.append(paths[j].name, paths[j]);
        }
        //其他参数
        formData.append("theme_name",vue.current_theme_name);
        formData.append("name",vue.media.name);
        formData.append("ctype",vue.media.type);
        formData.append("id",vue.id);
        var result = osrHttpUpload("PUT","/api/admin/theme/display-setting", formData);
        result.then(function (r) {
            if(r.data.msg_type=="s"){
                 //window.location.href='/osr-admin/theme-setting/display/'+vue.media.type+'-edit?cid='+vue.cid
                 //+'&id='+vue.id;
                location.reload();
            }
        });

    }


