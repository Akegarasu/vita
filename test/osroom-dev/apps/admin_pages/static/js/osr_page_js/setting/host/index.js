    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{hosts:[], "cmd_result":[]}
    })

    // 页面一加载完就自动执行
    $(document).ready(function(){
        get_host();
    });

    function get_host(){

       var result = osrHttp("GET","/api/admin/setting/sys/config/version",{}, args={not_prompt:true});
       result.then(function (r) {
            vue.hosts = r.data.hosts;
        });
    }

    function del_host(id){
        d = {
            ids:JSON.stringify([id])
        }
        var result = osrHttp("DELETE","/api/admin/setting/sys/host", d);
        result.then(function (r) {
            get_host();
        });

    }
