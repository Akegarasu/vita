
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