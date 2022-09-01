    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data: {
        username:'',
        password:'',
        cmd: '',
        port: 22,
        host_ip:""
      }
    })
    // 页面一加载完就自动执行
    $(document).ready(function(){

        get_host();
    });

    function get_host(){


        var ip = $("#ip").attr("content");
        vue.host_ip = ip;
        var d = {
            host_ip:ip
        }

        var result = osrHttp("GET","/api/admin/setting/sys/host",d, args={not_prompt:true});
       result.then(function (r) {
             vue.username = r.data.host.host_info.username;
            vue.password = r.data.host.host_info.password;
            vue.port = r.data.host.host_info.port;
            vue.cmd = r.data.host.cmd;
        });
    }

   function save_host(){
        var data = {
            username:vue.username,
            password:vue.password,
            cmd:vue.cmd,
            host_ip:vue.host_ip,
            host_port:vue.port

        }
        osrHttp("PUT","/api/admin/setting/sys/host", data);
   }


   function test_connect(){
        d = {
            host_ip:vue.host_ip
        }
        osrHttp("PUT","/api/admin/setting/sys/host/connection-test", d);
    }

