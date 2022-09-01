    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
            id:"",
            url:{methods:{}, custom_permission:{}},
            permissions:[],
            cnt:0,
            current_method:null
            }
    });
    // 加载完页面执行
    $(document).ready(function(){
        get_url();
        var result2 = osrHttp("GET","/api/admin/permission", {}, args={not_prompt:true});
        result2.then(function (r) {
            vue.permissions = r.data.permissions;
            vue.cnt = vue.permissions.length;
            vue.permissions = r.data.permissions;
        });
    })

    function get_url(){
        vue.id = $("#id").attr("content");
        d = {
            id:vue.id,
        }
        var result = osrHttp("GET","/api/admin/url/permission", d, args={not_prompt:true});
        result.then(function (r) {
            vue.url = r.data.url;
             if(vue.url.methods){
                vue.current_method = vue.current_method?vue.current_method:vue.url.methods[0];
            }
        });
    }

    function switch_method(value){
        vue.current_method = value;
    }
    //当点击提交按钮,提交用于填入的数据到api
    function update(method, uncustom){
        vue.current_method = method;
        var uncustom=uncustom?true:false;
        if(uncustom){
            var permission = [0];
        }else{
            var permission = $("#permission_"+method).val();
        }


        var login_auth = osr_get_checked_id();
        login_auth = login_auth.length?1:0;

        var d = {
            id:vue.id,
            method:method,
            login_auth:login_auth,
        }
        if(permission){
            d["custom_permission"] = JSON.stringify(permission);
        }
        // 提交数据
        var result = osrHttp("PUT","/api/admin/url/permission", d);
        result.then(function (r) {
            if (r.data.msg_type=="s"){
                get_url();
            }
        });
    }