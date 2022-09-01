    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
        navs:[],
        display_name:'',
        json_data:'',
        current_theme_name:null,
        lang:null,
        order:99
      },
      methods: {show_btn:show_btn}
    })

    // 加载完页面执行
    $(document).ready(function(){

        var url_s = get_url_parameter();
        vue.current_theme_name = get_obj_value(url_s, "theme", null);
        vue.lang = get_obj_value(url_s, "lang", null);
        get_navs();
    })

    function show_btn(id){
        alert(id)
        if( $("#"+id).hasClass("show") ){
            // 执行隐藏
            $("#"+id).hide().removeClass("show");
            // 其他
        }else{
            // 显示
            $("#"+id).show().addClass("show");
        }
    }

    function get_navs(){

        var result = osrHttp(
            "GET","/api/admin/theme/nav",
            {
                theme_name: vue.current_theme_name,
                language: vue.lang
            },
                args={not_prompt:true
            });
        result.then(function (r) {
            vue.navs = r.data.navs;
            $.each(vue.navs,function(n,value){
                value["json_data"] = JSON.stringify(value["json_data"]);
          });

        });

        var url = window.location.pathname+"?lang="+vue.lang;
        if(vue.current_theme_name){
            url = url + "&theme="+vue.current_theme_name;
        }
        history_state(title=null,url=url);

    }

    function switch_lang(value){
        vue.lang = value;
        get_navs();
    }

    function add(){

        var d = {
            display_name:vue.display_name,
            json_data:vue.json_data,
            theme_name: vue.current_theme_name,
            language: vue.lang,
            order: vue.order
        }
        // 提交数据
        var result = osrHttp("POST","/api/admin/theme/nav", d);
        result.then(function (r) {
            if (r.status=="success" && r.data.msg_type=="s"){
                get_navs();
                vue.display_name = "";
                vue.json_data = ""
            }
        });
    }

    function update(cid, display_name, json_data, order){

        var d = {
            id:cid,
            display_name:display_name,
            json_data:json_data,
            theme_name: vue.current_theme_name,
            language: vue.lang,
            order:order
        }
        // 提交数据
        var result = osrHttp("PUT","/api/admin/theme/nav", d);
        result.then(function (r) {
            if (r.status=="success" && r.data.msg_type=="s"){
                get_navs();
            }
        });
    }


    function del(id){

        var d = {
                 ids:JSON.stringify([id])
        }
        // 提交数据
        var result = osrHttp("DELETE","/api/admin/theme/nav", d);
        result.then(function (r) {
            if (r.status=="success" && r.data.msg_type=="s"){
                get_navs();
            }
        });
    }
