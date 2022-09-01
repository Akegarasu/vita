/*
    Author: Allen Woo
    Date: 2017-07-20
    Project: osroom css
    web site: www.osroom.com
*/

/*
    osroom封装的http请求
    各参数：
    type: 请求方式:GET, POST ,PUT, PATCH, DELETE等, 默认GET
    url:请求的api,
    data:请求的参数, 默认{}

    args:其他参数, 需要一个json {key:value}
        {
            async： <默认为true, 异步请求>
            location_href: <请求成功后需要跳转页面到哪个页面>
            not_prompt: <默认false, 为true时不再页面显示请求消息提示>
        }


    返回: 此封装方法返回一个Promise对象, 结果使用方式如
        var r = osrHttp("GET", "/api/xxxx", {}, {not_prompt:true});
        r.then(function (result) {
            //请求成功
            console.log('成功：' + result);
        }).catch(function (reason) {
            //请求失败
            console.log('失败：' + reason);
        });
*/
//请求主函数, 也可以直接调用
function osrHttp(type, url, data, args){

    type = type?type:"GET";
    data = data?data:{};
    var async = true;
    var location_href = null;
    var not_prompt = false
    //其他参数
    for(var k in args){
        if(k=="async"){
            async = args["async"]!=false?true:false;
        }else if(k=="location_href"){
            location_href = args["location_href"]?args["location_href"]:null;
        }else if(k=="not_prompt"){
            not_prompt = args["not_prompt"]?true:false
        }
    }
    var result = "";
    return new Promise(function(resolve,reject) {
        $.ajax({
              type : type,
              url : url,
              data : data,
              async : async,
              success : function(data, status,Thrown){
                    if(Thrown.status == 204){
                        data = {msg:"{{_('删除成功')}}", msg_type:"s"};
                    }
                    //消息弹出
                    if(!not_prompt || data.msg_type != "s"){
                        alert_msg(data);
                    }

                    if(location_href && data.msg_type == "s"){
                        location.href = location_href;
                    }else if(data.to_url){
                        location.href = data.to_url;
                    }
                    result = {data:data, status:"success"};
                    resolve(result);
              },
              error: function (XMLHttpRequest, textStatus, errorThrown) {
                    //消息弹出
                    data = $.parseJSON(XMLHttpRequest.responseText)
                    if(!not_prompt){
                        alert_msg(data);
                    }
                    if(data.to_url){
                        location.href = data.to_url;
                    }
                    result = {data:XMLHttpRequest.responseJSON, status:"error"};
                    reject(result);
              }
        });
    })
}

//文件上传
function osrHttpUpload(type, url, data, args){

    type = type?type:"GET";
    data = data?data:{};
    var async = true;
    var location_href = null;
    var not_prompt = false
    //其他参数
    for(var k in args){
        if(k=="async"){
            async = args["async"]!=false?true:false;
        }else if(k=="location_href"){
            location_href = args["location_href"]?args["location_href"]:null;
        }else if(k=="not_prompt"){
            not_prompt = args["not_prompt"]?true:false
        }
    }
    var name = data.name;
    if(data.get(data.get("name"))=="undefined"){
        var msg = {"msg":'{{_("请选择要上传的文件")}}', "msg_type":"e", "custom_status":400}
        alert_msg(msg);
        var result = {data:msg, status:"error"};

        return new Promise(function(resolve,reject) {
            resolve(result);
        });

    }else{
       return new Promise(function(resolve,reject) {
            $.ajax({
                type: type,
                url: url,
                data: data,
                async : async,
                processData: false,
                contentType: false,
                success : function(data, status,Thrown){
                    if(Thrown.status == 204){
                        data = {msg:"{{_('删除成功')}}", msg_type:"s"};
                    }
                    //消息弹出
                    if(!not_prompt || data.msg_type != "s"){
                        alert_msg(data);
                    }
                    if(location_href && data.msg_type == "s"){
                        location.href = location_href;
                    }else if(data.to_url && data.msg_type == "s"){
                        location.href = data.to_url;
                    }
                    result = {data:data, status:"success"};
                    resolve(result);
              },
              error: function (XMLHttpRequest, textStatus, errorThrown) {
                    //消息弹出
                    if(!not_prompt){ alert_msg($.parseJSON(XMLHttpRequest.responseText));}

                    result = {data:XMLHttpRequest.responseJSON, status:"error"};
                    reject(result);
              }
            });
       });
    }
}

/*
    请求结束消息显示
    页面中需要实现写好对应的msg-box和alert html
*/
function alert_msg(data){

    if (data.msg){
        var rint = parseInt(10000*Math.random());
        if(data.msg_type == "s"){
            var msg_id = 'success-'+rint;
            $('#msg-box').empty();
            $('#msg-box').append($('#alert-success').html());
            $('#success-msg').attr('id', msg_id);
            $("#"+msg_id).find("#success-msg-content").text(data.msg);
            var n = 1;//3s隐藏
            window.setInterval(
                function(){
                    if(!n){
                        $('#'+msg_id).remove();
                        return;
                    };
                    n -= 1;
                    // $("#"+msg_id).find("#success-msg-content").text(data.msg+" ("+n+"s)");
                },
            1000);

        }else if(data.msg_type == "w"){
            var msg_id = 'warning-'+rint;
            $('#msg-box').empty();
            $('#msg-box').append($('#alert-warning').html());
            $('#warning-msg').attr('id', msg_id);
            $("#"+msg_id).find("#warning-msg-content").text(data.msg);
            var n = 5;//3s隐藏
            window.setInterval(
                function(){
                    if(!n){
                        $('#'+msg_id).remove();
                        return;
                    };
                    n -= 1;
                },
            1000);

        }else if(data.msg_type == "e"){
            var msg_id = 'error-'+rint;
            $('#msg-box').empty();
            $('#msg-box').append($('#alert-error').html());
            $('#error-msg').attr('id', msg_id);
            $("#"+msg_id).find("#error-msg-content").text(data.msg);
        }
    }
}
/*
    模态确认框辅助函数
*/

//删除操作, 弹出确定模态框
function warning_modal(modal_data, onclick_func_name) {
    /*
    modal_data:json格式:如:{msg:xxx, modal_id:xxx, confirm_id:xxx}
    onclick_func_name: 点击事件调用函数的名称
    点击事件调用函数的参数放在以上2参数后面即可
    */
    var modal_data = modal_data?modal_data:{};
    var modal_id = modal_data.modal_id?'#'+modal_data.modal_id:'#osr-delete-modal';
    var confirm_id = modal_data.confirm_id?'#'+modal_data.confirm_id:'#confirm';
    var prompt_msg = modal_data.msg?modal_data.msg:null;
    var n = 0;
    var onclick = onclick_func_name+"(";
    for (var i in arguments) {
        if(n>1){
            var arg = arguments[i]
            if(typeof arg == "string"){
                arg = "'"+arg+"', ";
            }else if(typeof arg == "object"){
                arg = JSON.stringify(arg)+", ";
            }else{
                arg += ", ";
            }
            onclick += arg;
        }
        n += 1;
    }
    onclick += ")"
    // 绑定点击事件
    $(modal_id).find(confirm_id).attr("onclick", onclick);
    if(prompt_msg){
        $(modal_id).find("#prompt_msg").text(prompt_msg);
    }else{
        $(modal_id).find("#prompt_msg").text($(modal_id).find("#default_prompt_msg").text());
    }
    r = $(modal_id).modal("show");
 }

/*
    地址栏url操作系列函数
*/


// 获取url"?"后面的参数, 返回一个对象{key:value}
function get_url_parameter(url){

     url = url?url:null;
     // 获取url?后面参数, 并格式未json{}
     if(!url){
        url = window.location.search; //获取url中"?"符后的字串
     }else{
        url = "?"+url.split("?")[1]
     }
    var theRequest = new Object();
    if (url.indexOf("?") != -1) {
        var str = url.substr(1);
        strs = str.split("&");
        for(var i = 0; i < strs.length; i ++) {
          theRequest[strs[i].split("=")[0]] = decodeURI(strs[i].split("=")[1]);
        }
    }

   return theRequest;
};

// 获取一个{}对象对于key的值
function get_obj_value(dict, key, default_value){

    var v = dict[key];
    if(v==undefined || v=="undefined"){
        return default_value;
    }else{
        return v;
    }

}
// push到历史记录里，可以在点击后退时从历史记录里恢复内容
function history_state(title,url){

    // 并且无刷修改url地址
    if(title){
        $(document).attr("title",title);
    }

    if(history.pushState){
        var state=({url: url, title: title});

        window.history.pushState(state,title,url);
    }else{
        //如果不成功,使用老办法
        window.location = url;
    }

};
/*
    时间操作系列函数
*/
//获取当前时间，格式YYYY MM DD
function get_now_format_date(seperator1){

    var seperator1 = seperator1 ? seperator1 : '-';
    var date = new Date();
    var year = date.getFullYear();
    var month = date.getMonth() + 1;
    var strDate = date.getDate();
    if (month >= 1 && month <= 9) {
        month = "0" + month;
    }
    if (strDate >= 0 && strDate <= 9) {
        strDate = "0" + strDate;
    }
    var current_tdate = year + seperator1 + month + seperator1 + strDate;
    return current_tdate;
}

// 时间戳转日期
function formatDate (time, fmt) {
    var date = new Date(time*1000);
    if (/(y+)/.test(fmt)) {
        fmt = fmt.replace(RegExp.$1, (date.getFullYear() + '').substr(4 - RegExp.$1.length));
    }
    var o = {
        'M+': date.getMonth() + 1,
        'd+': date.getDate(),
        'h+': date.getHours(),
        'm+': date.getMinutes(),
        's+': date.getSeconds()
    };
    for (var k in o) {
        if (new RegExp(`(${k})`).test(fmt)) {
            var str = o[k] + '';
            fmt = fmt.replace(RegExp.$1, (RegExp.$1.length === 1) ? str : padLeftZero(str));
        }
    }
    return fmt;
};
function padLeftZero (str) {
    return ('00' + str).substr(str.length);
};
// 时间戳转不规则的日期
function irrformatDate (time, fmt) {

    var now_time = new Date().getTime();
    var diff_time = (now_time - time*1000)/1000; // 变为秒
    var tdate = new Date(time*1000);
    var now_date = new Date(now_time);

    var diff_y = now_date.getFullYear()-tdate.getFullYear();
    var diff_m = now_date.getMonth() - tdate.getMonth();
    var diff_d = now_date.getDate()-tdate.getDate();
    if(diff_time<60){
        tdate = "{{_('刚刚')}}";
    }else if(diff_time>=60 && diff_time<60*60){
        var t = diff_time/60;
        tdate = parseInt(t)+"{{_('分钟前')}}";
    }else if(diff_y==0 && diff_m==0 && diff_d == 0 && diff_time>=60*60){
        var t = diff_time/(60*60);
        tdate = parseInt(t)+"{{_('小时前')}}";
    }else if(diff_y==0 && diff_m==0 && diff_d == 1){
        temp_date = formatDate (time, fmt);
        tdate = "{{_('昨天')}}"+temp_date.slice(-5);
    }else if(diff_y == 0){
        tdate = formatDate(time, fmt).slice(5);
    }else{
        tdate = formatDate(time, fmt);
    }
    return tdate;

};

/*
    字符串处理系列函数
*/
// 格式字符串
function formatStr(key){
    // 首字母大写,_变" "
    var temp_key = key.replace("_", " ");
    temp_key = temp_key.replace(temp_key[0],temp_key[0].toUpperCase( ));
    return temp_key;
}

/*
    选择框处理函数
*/

/*  全选框 */
//datas: 要遍历的数据, checkAll==True全选,否则全不选
function osr_check_all(datas, checkAll) {
    if (checkAll) {
        //全选
        $("input[type='checkbox'], input[type='radio']").attr("checked",'true');
//        datas.forEach((item) => {
//            $("input[type='checkbox'], input[type='radio']").attr('checked', true);
//        });
    } else {
        //全不选
        $("input[type='checkbox'], input[type='radio']").removeAttr("checked");

//        datas.forEach((item) => {
//            $("input[type='checkbox'], input[type='radio']").attr('checked', false);
//        });
    }
}

//获取选中了的值
function osr_get_checked_id(){
    var ids = new Array();
    $("input:checkbox[type='checkbox']:checked").each(function(){
         if($(this).val() != 'on'){
            ids.push($(this).val());
         }
    })

    return ids;

}

/*
    针对OSROOM Api返回的分页数据进行分页导航处理
*/
//分页
function paging(page_total, current_page){
    if (page_total < 1){
        page_total = 1;
    }
    var next = current_page+1;
    var last = current_page-1;
    var last_show = [];
    var next_show = [];
    //last_show
    if(page_total>7 && current_page>=5){
        last_show =[1,2,'...',current_page-1]
    }else{
        for (var i=1;i<current_page;i++)
        {
            last_show.push(i);
        }
    }

    //next_show
    if(page_total>7 && current_page<page_total-2){
        next_show =[current_page+1,"...",page_total-1,page_total]
    }else{
        for (var i=page_total;i>current_page;i--)
        {
            next_show.splice(0, 0, i);
        }
    }
    return {page_total:page_total, next:next, last:last, next_show:next_show, last_show:last_show, current_page:current_page}
}

/*
    其他常用函数
*/

// 获取{}对象所有的key, 返回数组
function get_obj_keys(obj){
    var keys = [];
    for(var i in obj) {
        keys.push(i);
    }
    return keys;
}
// 生成唯一UID
function S4() {
    return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
}
function osr_guid() {
   return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
}


/*
    加载网页后自动执行的函数
*/

// header菜单 active
$(function(){
    var url = window.location.href.split("?")[0];
    var tag_li = "";
    var tag_a1 = "";
    var is_brack = 0
    $('#navbar_left').find("li").each(function () {
        $(this).find(".lv1-a").each(function () {
            if (this.href == url) {
                $(this).addClass('active');
                is_brack = 1;
                return false;
            }else{
                lv1_a = this;
            }
        });

        $(this).find("ul").each(function () {
            $(this).find("li").each(function () {
                $(this).find("a").each(function () {
                    if (this.href == url) {
                        $(lv1_a).addClass('active');
                        $(this).addClass('active');
                        is_brack = 1;
                        return false;
                    }
                });
            });
         });
        if (is_brack){ return false;}
    });

    //滚动检测
    // var top_height = $("#top-nav").height();
    // var top_nav = $('#top-nav');
    // var btn_go_up = $('#go-up')
    // var added = false;
    // $(window).scroll(function(){
    //     var this_scrollTop = $(this).scrollTop();
    //     if(!added && this_scrollTop>=top_height ){
    //         top_nav.addClass('osr-top-navbar');
    //         top_nav.removeClass('navbar');
    //         added = true;
    //         btn_go_up.show()
    //     }else if(added && this_scrollTop<top_height-5){
    //         top_nav.addClass('navbar');
    //         top_nav.removeClass('osr-top-navbar');
    //         added = false;
    //         btn_go_up.hide()
    //     }
    // });


});

// 内部导航bar active
function nav_active(head_tag_id, content_tag_id) {
    $('#'+head_tag_id).addClass("active");
    if(content_tag_id){
        $('#'+content_tag_id).addClass("active");
    }
}

// btn导航bar active
function nav_btn_active(p_tag_id, tag_id){
    //p_tag_id 父级标签ID
     $("#"+p_tag_id).find(".osr-btn").each(function () {
         $(this).removeClass('osr-btn-active');
     });
    $("#"+tag_id).addClass('osr-btn-active')
}

// tooltip初始化
$(function(){
    $('[data-toggle="popover"]').popover();
});
$(function() {
    $("body").tooltip({ selector: '[data-toggle=tooltip]' });
});

//鼠标划过下拉菜单
//$(function(){
//    var $dropdownLi = $('li.dropdown');
//    $dropdownLi.mouseover(function() {
//        $(this).addClass('open');
//    }).mouseout(function() {
//        $(this).removeClass('open');
//    });
//});

/*
    表单验证, 需要引入bootstrapValidator.min.js先
    Author:Allen Woo
    Date: 2018-04-14
*/
$(function(){
    formValid();
})
function formValid(id, submitButtons) {

    if(!id){
        var id = "body";
    }else{
        var id = "#"+id
    }
    if(!submitButtons){
        var submitButtons = ".osr-submit-btn";
    }
    form = $(id).bootstrapValidator({
        excluded: [':disabled', ':hidden', ':not(:visible)'],
        feedbackIcons: null,
        /**
        * 生效规则（三选一）
        * enabled 字段值有变化就触发验证
        * disabled,submitted 当点击提交时验证并展示错误信息
        */
        live: 'enabled',
        /**
        * 为每个字段指定通用错误提示语
        */
        message: 'This value is not valid',
        /**
        * 指定提交的按钮，例如：'.submitBtn' '#submitBtn'
        * 当表单验证不通过时，该按钮为disabled
        */
        submitButtons: submitButtons,
        submitHandler: null,
        /**
        * 为每个字段设置统一触发验证方式（也可在fields中为每个字段单独定义），默认是live配置的方式，数据改变就改变
        * 也可以指定一个或多个（多个空格隔开） 'focus blur keyup'
        */
        trigger: "focus blur keyup",
        /**
        * Number类型  为每个字段设置统一的开始验证情况，当输入字符大于等于设置的数值后才实时触发验证
        */
        threshold: null,
        /**
        * 表单域配置
        */
        fields: null
    });

    formValidate = function(){
        var bootstrapValidator = form.data('bootstrapValidator');
        //手动触发验证
        bootstrapValidator.validate();
    }

}

/*
    常用的api 请求操作
*/
//退出登录
function sign_out(){
    result = osrHttp("GET","/api/sign-out");
    result.then(function(r){
        if(r.data.msg_type == "s"){
            window.location = r.data.to_url;
        }
    });

}
// 切换语言
function set_language(lan){

    var d = {
        language:lan
    }
    result = osrHttp("PUT","/api/session/language-set", d,{not_prompt:true});
    result.then(function(r){
        if(r.data.msg_type=="s"){
            location.reload(true);
        }
    });

}

// 举报内容违规
function content_inform(cid, ctype, category, details){
    d = {
        cid:cid,
        ctype:ctype,
        category:category,
        details:details
    }
    osrHttp("PUT","/api/inform/content",d);
}

function osr_colors(){
    var colors = ['#CCCC66','#336666','#CC99CC', '#CC9933',
       '#666699','#CCFF66',
       '#999999', '#66CC99', '#CCFF99', '#003366',
       '#CCFFCC', '#666666', '#FF99CC',
       '#3399CC',  '#CC99CC', '#CC9933',
       '#000000', '#339999', '#FFCC33', '#009999',
       '#CC3333', '#999966', '#996699', '#669999',
       '#CCCC99', '#336699', '#003333',
       '#FFCC00', '#99CCFF', '#99CC99', '#66CCCC', '#663333']
    return colors
}