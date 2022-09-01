    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data: {
        host_info:{},
        cmd: '',
        cmd_result:{}
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
            vue.host_info = r.data.host.host_info;
            vue.cmd = r.data.host.cmd;
       });
    }

    function exec_cmd(cmd){
        d = {
            host_ip:vue.host_info.local_ip,
            cmd:cmd
        }

        var result = osrHttp("PUT","/api/admin/setting/sys/host/cmd-execute", d);
        result.then(function (r) {
            if(r.data.msg_type=="s"){
                vue.cmd_result = r.data.result;
            }
        });

    }


