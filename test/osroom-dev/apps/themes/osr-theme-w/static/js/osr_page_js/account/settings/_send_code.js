
   function get_imgcode(){
        var result = osrHttp("GET","/api/vercode/image",{},args={not_prompt:true});
        result.then(function (r) {
            if(r.data.code){
                vue.img_code_url = r.data.code.url;
                vue.img_code_url_obj = r.data.code.img_url_obj;
            }
        });

   }

   function send_code(){

        //查看邮箱是否可以使用
        var d = { value:vue.email, field:"email"};
        var result = osrHttp("GET","/api/account/data/availability",d);
        result.then(function (r) {
            if(r.data.msg_type == "s"){
                //邮件可用
                if(!vue.current_email_send_success){
                    d = {
                        account:"{{current_user.email}}",
                        account_type:"email",
                        code:vue.img_code,
                        code_url_obj:JSON.stringify(vue.img_code_url_obj)
                    };

                    // 提交数据
                    var result = osrHttp("POST", "/api/vercode/send", d);
                    result.then(function (r) {
                        vue.current_email_send_success=1;
                        send_success_process(r);
                    }).catch(function(r){
                        send_failed(r);
                    });
                }

                if(!vue.new_email_send_success){
                    d2 = {
                        account:vue.email,
                        account_type:"email",
                        code:vue.img_code,
                        code_url_obj:JSON.stringify(vue.img_code_url_obj)
                    };
                    var result2 = osrHttp("POST", "/api/vercode/send", d2);
                    result2.then(function (r) {
                        vue.new_email_send_success=1;
                        send_success_process(r);
                    }).catch(function(r){
                        send_failed(r);
                    });
               }

            }
        });
   }

   function send_success_process(r){
        //发送成功
        if(r.data.msg_type=="s"){
            //发送成功
            $("#send_code_div").hide();//模态框
            $("#send_code_2_div").show();

            //验证码发送成功, 关闭已经打开的模态框(如果已经打开)
            $('#send_code_modal').modal('hide');

            if(vue.new_email_send_success && vue.current_email_send_success){
                $("#send_code_2").attr("disabled","disabled");
                var n = 60;
                window.setInterval(
                    function(){
                        if(!n){
                            $("#send_code_2").attr("disabled",false);
                            $('#send_code_2').text("{{_('发送验证码')}}")
                            return;
                        };
                        $('#send_code_2').text(n+"s{{_('后重发')}}")
                        n -= 1;
                    },
                1000);
            }
        }
   }

   function send_failed(r){

        var temp_code = null;
        if(r.data.code){
            temp_code = r.data.code;
        }else if(r2.data.code){
            temp_code = r2.data.code;
        }
        if(temp_code){
            //图片验证码错误, 需要输入图片验证码 打开模态框,
            $('#send_code_modal').modal('show');
            vue.img_code_url = temp_code.url;
            vue.img_code_url_obj = temp_code.img_url_obj;
            $("#send_code_div").show();
            $("#send_code_2_div").hide();
        }
   }
