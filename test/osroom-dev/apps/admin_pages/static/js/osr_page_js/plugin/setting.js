    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
        confs:[{}],
        plugin:"",
        plugin_info:{}
      },
      filters: {
            formatDate: function (time) {

              return formatDate(time, "yyyy-MM-dd hh:mm");
            },
            formatKey: function (key) {
              return formatStr(key);
            }
      }
    });

    var from_page = $("#from_page").attr("content");
    // 页面一加载完就自动执行
    $(document).ready(function(){

        var plugin = $("#plugin").attr("content");
        vue.plugin = plugin?plugin:vue.plugin;
        get_confs();
    });


    function get_confs(){

      //获取数据
      d = {
        plugin_name:vue.plugin
      }

      var result = osrHttp("GET","/api/admin/plugin/setting", d, args={not_prompt:true});
        result.then(function (r) {
          vue.confs = r.data.configs;
          vue.plugin_info = r.data.plugin_info;
          $.each(vue.confs,function(n,value){
                if(value["type"] == "dict"){
                    $.each(value["value"],function(k,value2){
                        value["value"][k] = JSON.stringify(value2);
                    });
                }
          });
      });
      var url = window.location.pathname+"?plugin="+vue.plugin+"&from_page="+from_page;
      history_state(title=null ,url=url);
    }

    function post_conf(key, index){

        var value = vue.confs[index].value;
        if(vue.confs[index].value_type == "bool"){
            value = $("#"+vue.confs[index]._id+" option:selected").val();
        }

        if(vue.confs[index].value_type == "list"){
            //数组
            var value = [];
            var txt = $('#list_'+vue.confs[index].key).find('input'); // 获取所有文本框
            for (var i = 0; i < txt.length; i++) {
                value.push(txt.eq(i).val()); // 将文本框的值添加到数组中
            }
            value = JSON.stringify(value);

        }else if(vue.confs[index].value_type == "dict"){
            //字典
            var value = {};
            // 获取所有的字典一级key
            var key_txt = $('#dict_'+vue.confs[index].key).find('input');
            // 获取所有的字典一级value
            var value_txt = $('#dict_'+vue.confs[index].key).find('textarea');

            // 遍历把key和value结合
            for (var i = 0; i < key_txt.length; i++) {
                temp_key = key_txt.eq(i).val();
                if(!temp_key){
                    alert_msg({"msg":"Key不能为空", "msg_type":"e"});
                    return;
                }
                try{
                    var temp_val = JSON.parse(value_txt.eq(i).val());
                }catch(e){
                    var temp_val = value_txt.eq(i).val();
                }
                value[temp_key]= temp_val
            }
            value = JSON.stringify(value);
        }


        d = {
            plugin_name:vue.plugin,
            key:key,
            value:value

        }
        var result = osrHttp("PUT","/api/admin/plugin/setting", d);
        result.then(function (r) {
            if (r.data.msg_type == "s"){
                location.reload();
                //$(".list_dict").remove();
            }
        });
    }

    function refresh_conf(){

      //获取数据
      d = {
        plugin_name:vue.plugin
      }

       var result = osrHttp("POST","/api/admin/plugin/setting", d);
        result.then(function (r) {
            if (r.data.msg_type == "s"){
                location.reload();
                //$(".list_dict").remove();
            }
        });
    }

    function install_requs(){
      d = {
        plugin_name:vue.plugin
      }
      var result = osrHttp("PUT","/api/admin/plugin/setting/install-requirement", d);
      result.then(function (r) {
            if(r.data.msg){
                get_confs();
              }
      });
    }

