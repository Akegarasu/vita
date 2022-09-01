var upload_data = {
    name:"{{_('批量上传')}}",
    ctype:vue.media_type,
    batch:1,
    category_name:"{{_('默认')}}"
}
//加载完页面立即执行
$(document).ready(function(){

    var cid = $("#cid").attr("content");
    if(vue.cid=="null" || vue.cid == undefined){
        vue.cid = ""
    }
    vue.curren_category = cid;
    get_category();
    var page = $("#page").attr("content");
    vue.page = page?page:vue.page;
    var sort = $("#sort").attr("content");
    vue.sort = sort?sort:vue.sort;
    var keyword = $("#keyword").attr("content");
    vue.keyword = keyword?keyword:vue.keyword;
    get_media(vue.page, vue.keyword);

});
$("#start-upload").click(function(){
    $("#upload-html").toggle();
    if(!$("#upload-html").is(":hidden")){
        init_upload(uploader_conf(upload_data), {"X-CSRFToken":csrftoken});
        $("#start-upload-text").text("{{_('关闭上传')}}");
        $("#category-select").attr("disabled", true);
    }else{
        $("#start-upload-text").text("{{_('上传')}}");
        $("#category-select").removeAttr("disabled");
        get_media(1,'');
    }
});

//获取分类
function get_category(){

    var result = osrHttp("GET","/api/admin/content/category",{type:vue.media_type},args={not_prompt:true});
    result.then(function (r) {
        vue.media_categorys = r.data.categorys;
    });
}

//获取媒体数据
function get_media(page, keyword, sort_field){
    vue.page = page;
    vue.keyword = keyword;

    var sort = sorting(sort_field);

    var d = {
        ctype:vue.media_type,
        category_id:vue.curren_category,
        keyword:vue.keyword,
        page:vue.page,
        pre:12,
        sort:JSON.stringify(sort)
    }

    var result = osrHttp("GET","/api/admin/upload/media-file",d,args={not_prompt:true});
    result.then(function (r) {
        vue.medias = r.data.medias;
        vue.checkAll = false;
        my_check_all();
        vue.pages = paging(page_total=vue.medias.page_total,
        current_page=vue.medias.current_page);
    });

    var url = window.location.pathname+"?page="+page+"&cid="+vue.curren_category+"&sort="+vue.sort;
    if(vue.keyword){
        url = url + "&keyword="+vue.keyword;
    }
    history_state(title=null,url=url);
}

//删除媒体数据
function del_media(){
    var ids = osr_get_checked_id();

    if(ids.length){
        ids = JSON.stringify(ids);
        var d = {
            ids:ids
        }

        var result = osrHttp("DELETE","/api/admin/upload/media-file", d);
        result.then(function (r) {
            if(r.data.msg_type="s"){
                get_media();
            }
        });

    }else{
        alert_msg({msg:'{{_("请选择要删除的项")}}', msg_type:"w"});
    }
}

//切换分类
function switch_category(value) {
    vue.curren_category = value.split("___")[0];
    get_media(1, "");
    upload_data["category_id"] = vue.curren_category;
    upload_data["category_name"] = value.split("___")[1];
    if(!$("#upload-html").is(":hidden")){
        init_upload(uploader_conf(upload_data), {"X-CSRFToken":csrftoken});
    }
}

//全选
function my_check_all(){

    osr_check_all(vue.medias.datas, vue.checkAll);
    if(vue.checkAll){
        $("#check-btn-text").text("{{_('取消全选')}}");
    }else{
        $("#check-btn-text").text("{{_('全选')}}");
    }
    if(vue.media_type == "image" || vue.media_type == "video"){
        vue.checkAll = !vue.checkAll;
    }

}

function sorting(sort_field){
    // 反转排序
    if(sort_field=="time"){
        if(vue.sort == "time-desc"){
            vue.sort = "time-asc";
        }else{
            vue.sort = "time-desc";
        }
    }else if(sort_field=="inform"){
        if(vue.sort == "inform-desc"){
            vue.sort = "inform-asc";
        }else{
            vue.sort = "inform-desc";
        }
    }

    //排序参数
    if(vue.sort=="time-desc"){
        sort = [{"time":-1}];

    }else if(vue.sort=="time-asc"){
        sort = [{"time":1}];

    }else if(vue.sort=="inform-desc"){
        sort = [{"inform.total":-1}];

    }else if(vue.sort=="inform-asc"){
        sort = [{"inform.total":1}];

    }
    return sort;
}

 function put_media_view(inform){
    console.log(inform)
    vue.inform = inform;
}
