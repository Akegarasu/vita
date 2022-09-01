    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
            url:null
            }
    })

    function add(){
        formValidate();
        d = {
            url:vue.url,
        }

        var result = osrHttp("POST","/api/admin/url/permission", d);
        result.then(function (r) {
            if (r.status=="success" && r.data.msg_type=="s"){
                 location.href = "/osr-admin/permission/url/edit?id="+r.data.inserted_id
                                    +"&ft="+$("#ft").attr("content")
                                    +"&fp="+$("#fp").attr("content")
            }
        });

    }

