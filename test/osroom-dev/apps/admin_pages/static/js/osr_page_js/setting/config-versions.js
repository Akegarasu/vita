    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{version:{}, hosts:[], must_restart:true},
      filters: {
            formatDate: function (time) {
              if(time){
                return formatDate(time, "yyyy-MM-dd hh:mm:ss");
              }
              return "";
            }
      }
    })

    // 页面一加载完就自动执行
    $(document).ready(function(){

        get_version();
    });

    function get_version(){

      var result = osrHttp("GET","/api/admin/setting/sys/config/version", {}, args={not_prompt:true});
      result.then(function (r) {
        vue.version = r.data.version;
        vue.hosts = r.data.hosts;
      });

    }

    function post_switch(index){
        var rollback = $("#rollback"+index+ " option:selected").val();

        var update = $("#update"+index+ " option:selected").val();
        if (update=="1"){
            update = 0;
        }else{
            update = 1;
        }

        var ip = vue.hosts[index].host_info.local_ip
        d = {
            switch_version:rollback,
            disable_update:update,
            host_ip:ip
        }
        var result = osrHttp("PUT","/api/admin/setting/sys/config/version", d);
        result.then(function (r) {
            if (r.data.msg_type == "s"){
                get_version();
            }
        });
    }
