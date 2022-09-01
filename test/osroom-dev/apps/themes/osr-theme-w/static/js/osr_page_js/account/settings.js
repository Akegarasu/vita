
/* main */
var vue = new Vue({
  el: '#app',
  delimiters:['{[', ']}'],
  data:{
        user_profile:{
            avatar_url:{}
        },
        birthday:null,
        set:"profile",
        input_domain:""
        }
})

// 页面一加载完就自动执行
$(document).ready(function(){
      var set = $("#user_set").attr("content");
      vue.set = set?set:vue.set;
      nav_active("head_li_"+vue.set, vue.set);
      get_profile();
});

function switch_type(set){
    vue.set = set;
    get_profile();
}

function get_profile(){

     if(vue.set != "basis"){
        $("#user-basis").hide();
        $("#user-profile").show();
     }else{
        $("#user-profile").hide();
        $("#user-basis").show();
     }

     var result = osrHttp("GET","/api/account/profile",{}, args={not_prompt:true});
    result.then(function (r) {
          vue.user_profile = r.data.user;
          vue.birthday = r.data.user.birthday;

          var email_list = vue.user_profile.email.split("@");
          vue.user_profile.email = email_list[0].slice(0,3)+"****"+email_list[0].slice(-3)+"@"+email_list[1];
          if(!vue.birthday){
            vue.birthday = get_now_format_date();
          }else{
              var y = parseInt(vue.birthday/10000);
              var m = parseInt(vue.birthday/100)%100
              if (m < 10){
                m = "0" + m;
              }
              var d = vue.birthday%100;
              if (d < 10){
                d = "0" + d;
              }
              vue.birthday = y+'-'+m+'-'+d;
          }
    });

    var url = window.location.pathname+"?set="+vue.set;
    if(vue.set=="profile" || !vue.set){
        var title= "{{_('个人资料')}}"

    }else{
        var title= "{{_('基础设置')}}"
    }

    history_state(title+"-{{g.site_global.site_config.TITLE_SUFFIX}}", url);
}

function ready_add_domain(){
    if(vue.input_domain){
        vue.input_domain = 0;
    }else{
        vue.input_domain = 1;
    }
}


/* prifile */
$(function(){

    $.fn.datetimepicker.dates['zh-CN'] = {
            days: ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"],
            daysShort: ["周日", "周一", "周二", "周三", "周四", "周五", "周六", "周日"],
            daysMin:  ["日", "一", "二", "三", "四", "五", "六", "日"],
            months: ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
            monthsShort: ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
            today: "今天",
            suffix: [],
            meridiem: ["上午", "下午"]
    };

    var current_lang = '{{g.site_global.language.current}}';

    if(current_lang=="zh_CN"){
        current_lang = "zh-CN";
    }else{
        current_lang = "EN";
    }
    $("#birthday").datetimepicker(
        {
        todayBtn : true,
         format: 'yyyy-mm-dd',
         weekStart:1,
        initialDate: vue.birthday,
        startDate: "1900-01-01",
        startView:4,
        minView : "month",
        maxView:4,
        todayHighlight:true,
        keyboardNavigation:true,
        language:current_lang,
        autoclose:true
        }
    );
});

//当点击提交按钮,提交用于填入的数据到api
function save_profile(){
    var reg = new RegExp("-","g");//g,表示全部替换
    var birthday = $('#birthday').val().replace(reg,"");
    if(!birthday){
        birthday = vue.birthday.replace(reg,"");
    }
    d = {
        gender:vue.user_profile.gender,
        homepage:vue.user_profile.homepage,
        info:vue.user_profile.introduction,
        birthday:birthday
    }
    // 提交数据
    var result = osrHttp("PUT", '/api/account/profile', d);
    result.then(function (r) {
        if(r.data.msg_type=="s"){
            get_profile();
        }
    });
}

/* basic */
//当点击提交按钮,提交用于填入的数据到api
function save_basic(){
    if (vue.user_profile.custom_domain==-1){
        var d = {
                username:vue.user_profile.username,
                editor:vue.user_profile.editor}
    }else{
        var d = {
                 username:vue.user_profile.username,
                 custom_domain:vue.user_profile.custom_domain,
                 editor:vue.user_profile.editor
                 }
    }
    // 提交数据
    var result = osrHttp("PUT", "/api/account/basic", d);
    result.then(function (r) {
        if(r.data.msg_type=="s"){
            get_profile();
        }
    });

}

$(function(){
    imageObj = avatar_cut_upload(
        img_id="ava-image",
        btn_input_img_id="inputImage"
       )
});

function avatar_upload(){
    var data = $("#upload_avatar").data();
    var result = imageObj.cropper(data.method, data.option, data.secondOption);
    switch (data.method) {

        case 'getCroppedCanvas':
        if (result) {

           // 上传头像
           //alert($('#inputImage')[0].files.length)
            var d = {
                imgfile_base:result.toDataURL('image/png'),

            }

            var result = osrHttp("PUT", "/api/account/upload/avatar", d);
            result.then(function (r) {
                if(r.data.msg_type=="s"){
                    get_profile();
                }
            });
        }
        break;
    }

}



