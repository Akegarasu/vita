    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{confs:[],
           projects:[],
           current_project:"all",
           keyword:"",
           is_search_results:0,
           must_restart:true,
           config_info:null,
           config_name:"All"
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

    // 页面一加载完就自动执行
    $(document).ready(function(){

        var d = {
            project_info:1,
            project_info_page:1,
            project_info_pre:1000,
        }

        var result = osrHttp("GET","/api/admin/setting/sys/config", d, args={not_prompt:true});
        result.then(function (r) {
            vue.projects = r.data.projects.datas;
            var current_project = $("#project").attr("content");
            vue.current_project = current_project?current_project:vue.current_project;


            var keyword = $("#keyword").attr("content");
            vue.keyword = keyword?keyword:vue.keyword;

            if(vue.current_project){
                if(vue.current_project=="all"){
                    get_confs("all");
                }else{
                    get_confs([vue.current_project]);
                }

            }else{
                get_confs([vue.projects[0]]);
            }
         });
    });


    function get_confs(project){

      //获取数据
      if(project == "all"){
        project = [];
        vue.current_project = "all";
      }else{
        vue.current_project = project[0];
      }

      vue.is_search_results = vue.keyword;
      var d = {
        project:JSON.stringify(project),
        keyword:vue.keyword
      }

      var result = osrHttp("GET","/api/admin/setting/sys/config", d, args={not_prompt:true});
      result.then(function (r) {

          vue.confs = r.data.configs;
          if (project[0]){
                vue.config_name = project[0];
          }else{
                vue.config_name = "all";
          }

          if (vue.confs){
                if (vue.confs[0]["__restart__"] == "must"){
                    vue.must_restart = 1;
                }else{
                    vue.must_restart = 0;
                }
                vue.config_info = vue.confs[0]["__info__"]

          }
          $.each(vue.confs,function(n,value){
                if(value["type"] == "dict"){
                    $.each(value["value"],function(k,value2){
                        value["value"][k] = JSON.stringify(value2);
                    });
                }
          });
       });

        var url = window.location.pathname+"?project="+vue.current_project;
        if(vue.keyword){
            url = url + "&keyword="+vue.keyword;
        }
        history_state(title=null ,url=url);
    }

    function post_conf(project, key, index){

        var value = vue.confs[index].value;
        if(vue.confs[index].type == "bool"){
            value = $("#"+vue.confs[index]._id+" option:selected").val();
        }

        if(vue.confs[index].type == "list"){
            //数组
            var value = [];
            var txt = $('#list_'+vue.confs[index].key).find('input'); // 获取所有文本框
            for (var i = 0; i < txt.length; i++) {
                value.push(txt.eq(i).val()); // 将文本框的值添加到数组中
            }
            value = JSON.stringify(value);

        }else if(vue.confs[index].type == "dict"){
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
                    alert_msg({"msg":"{{_('Key不能为空')}}", "msg_type":"e"});
                    return;
                }
                try{
                    var temp_val = JSON.parse(value_txt.eq(i).val());
                }catch(e){
                    var temp_val = value_txt.eq(i).val();
                    if(!temp_val){
                        alert_msg({"msg":"{{_('Value不能为空')}}", "msg_type":"e"});
                        return;
                    }
                     // alert_msg({"msg":'['+temp_key+"]{{_('的value格式错误,请检查')}}", "msg_type":"e"});
                     // return;
                }
                value[temp_key]= temp_val
            }
            value = JSON.stringify(value);
        }

        d = {
            project:project,
            key:key,
            value:value,
        }

        var result = osrHttp("PUT","/api/admin/setting/sys/config", d);
        result.then(function (r) {
            if (r.data.msg_type == "s"){
                location.reload();
                //$(".list_dict").remove();
            }
        });
    }


