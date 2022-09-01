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
           type:media_type
    },
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
    vue.category_id = $("#cid").attr("content")
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

    var result = osrHttp("GET","/api/admin/content/category",{type:vue.media.type},args={not_prompt:true});
    result.then(function (r) {
        vue.media_categorys = r.data.categorys;
    });
}

//获取
function get_media(){
    var d = {
        id:vue.id
    }

    var result = osrHttp("GET","/api/admin/upload/media-file",d,args={not_prompt:true});
    result.then(function (r) {
        vue.media = r.data.media;
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
         name:vue.media.name,
         title:vue.media.title,
         ctype:vue.media.type,
         link:vue.media.link,
         link_open_new_tab:vue.media.link_open_new_tab,
         link_name:vue.media.link_name,
         text:vue.media.text,
         text_html:vue.media.html
    }
    if(vue.new_category_id){
        d["category_id"] = vue.new_category_id;
        vue.new_category_id = null;
    }

    // 提交数据
    if(vue.id){
        //更新
        d["id"] = vue.id
        var result = osrHttp("PUT","/api/admin/upload/media-file", d);
        result.then(function (r) {
            if(r.data.msg_type=="s"){
                 //window.location.href='/osr-admin/media/'+vue.media.type+'-edit?cid='+vue.cid
                 //+'&id='+vue.id;
                 location.reload();
            }
        });

    }else{
        //添加
        var result = osrHttp("POST","/api/admin/upload/media-file", d);
        result.then(function (r) {
            if(r.data.msg_type == "s"){
                window.location.href='/osr-admin/media/'+vue.media.type+'?cid='+vue.cid;
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
    formData.append("name",vue.media.name);
    formData.append("ctype",vue.media.type);
    formData.append("id",vue.id);

    var result = osrHttpUpload("PUT","/api/admin/upload/media-file", formData);
    result.then(function (r) {
        if(r.data.msg_type=="s"){
             window.location.href='/osr-admin/media/'+vue.media.type+'-edit?cid='+vue.cid
             +'&id='+vue.id;
        }
    });

}