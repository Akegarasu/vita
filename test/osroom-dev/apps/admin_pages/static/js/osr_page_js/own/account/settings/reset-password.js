    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data: {
        username:'',
        email:'',
        now_password:'',
        password: '',
        password2: '',
      }
    })

    $(document).ready(function(){

    });

    function reset(){
        formValidate();
        var d = {now_password:vue.now_password,
                    password:vue.password,
                    password2:vue.password2};
        // 提交数据
        osrHttp("PUT", "/api/account/password/reset", d);
    }

