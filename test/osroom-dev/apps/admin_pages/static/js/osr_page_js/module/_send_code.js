
   function get_imgcode(){

        var result = osrHttp("GET","/api/vercode/image", {}, args={not_prompt:true});
        result.then(function (r) {
            if(r.data.msg_type=="s"){
                if(r.data.code){
                    vue.img_code_url = r.data.code.url;
                    vue.img_code_url_obj = r.data.code.img_url_obj;
                }
            }
        })
   }

   function send_code(){

        d = {
            account:vue.email,
            account_type:"email",
            code:vue.img_code,
            code_url_obj:JSON.stringify(vue.img_code_url_obj),

        }
        if(vue.send_code_to_exist_account){
            d["exist_account"] = 1;
        }
        // 提交数据
        var result = osrHttp("POST","/api/vercode/send", d);
        result.then(function (r) {
            if(r.data.msg_type=="s"){
                //发送成功
                $("#send_code_div").hide();
                $("#send_code_2_div").show();

                //验证码发送成功, 关闭已经打开的模态框(如果已经打开)
                $('#send_code_modal').modal('hide');

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
         }).catch(function (r) {

                if(r.data.code){
                    //图片验证码错误, 需要输入图片验证码 打开模态框,
                    $('#send_code_modal').modal('show');
                    vue.img_code_url = r.data.code.url;
                    vue.img_code_url_obj = r.data.code.img_url_obj;
                    $("#send_code_div").show();
                    $("#send_code_2_div").hide();
                }
         });

    }

