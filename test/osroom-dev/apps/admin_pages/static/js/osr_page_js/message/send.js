    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
          msg:{send_type:["on_site"],
               content:"",
               content_html:"",
               title:""
          },
          username:null,
          confirm_send:""
      },
    })

    // 加载完页面执行
    $(document).ready(function(){

        editor.txt.html("");
    })


    function send(){
        formValidate();
        if(vue.confirm_send=="Send"){
            vue.msg.content = editor.txt.text();
            vue.msg.content_html = editor.txt.html();
            vue.msg.send_type = JSON.stringify(osr_get_checked_id());
            d = vue.msg;
            if(vue.username){
                d["username"] = JSON.stringify(vue.username.split(";"));
            }

            osrHttp("POST","/api/admin/message/send", d);
            vue.confirm_send = "";
        }else{
            alert("{{_('确认失败,未发送')}}");
        }
    }

