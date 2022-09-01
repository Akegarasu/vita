    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data: {
        email:'',
        password: '',
        new_email_code:'',
        current_email_code:'',
        img_code_url_obj:{},
        img_code_url:"",
        img_code:"",
        current_email_send_success:0,
        new_email_send_success:0
      }
    })

    function reset(){
        formValidate();
        var d = {   code:vue.code,
                    new_email_code:vue.new_email_code,
                    current_email_code:vue.current_email_code,
                    email:vue.email,
                    password:vue.password};
        // 提交数据
        osrHttp("PUT", "/api/account/email", d);
    }

