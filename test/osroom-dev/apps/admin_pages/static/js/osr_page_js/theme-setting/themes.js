
    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
          themes:[],
          img_w_h:"?w=0&h=720",
      },
      filters: {
            formatDate: function (time) {
              return irrformatDate(time, "yyyy-MM-dd hh:mm");
            }
      }
    })

    // 加载完页面执行
    $(document).ready(function(){

        get_themes();

    })

    function get_themes(){
       var d = {}
       var result = osrHttp("GET","/api/admin/theme",d, args={not_prompt:true});
       result.then(function (r) {
            vue.themes = r.data.themes;
       });

    }

    function upload_theme(){
        var formData = new FormData();
        var name = $("#upfile").attr("name");
        formData.append("upfile", $("#upfile")[0].files[0]);
        var result = osrHttpUpload("POST","/api/admin/theme", formData);
        result.then(function (r) {
            if(r.data.msg_type=="s"){
                get_themes();
            }
        });
    }

    function restore(name){
        var d = {
            theme_name:name,
            restore_deled:1
        }
        var result = osrHttp("PUT","/api/admin/theme", d);
        result.then(function (r) {
            if(r.data.msg_type=="s"){
                get_themes();
            }
        });
    }


    function delete_theme(name){
        var d = {
            theme_name:name
        }
        var result = osrHttp("DELETE","/api/admin/theme", d);
        result.then(function (r) {
            if(r.data.msg_type=="s"){
                get_themes();
            }
        });
    }


    function switch_theme(name){
        var d = {
            theme_name:name
        }
        var result = osrHttp("PUT","/api/admin/theme", d);
        result.then(function (r) {
            if(r.data.msg_type=="s"){
                get_themes();
            }
        });
    }

    $(function() {
        $('#upfile').on('change', function() {
          var fileNames = '';
          $.each(this.files, function() {
            fileNames += '<span class="badge">' + this.name + '</span> ';
          });
          $('#file-list').html(fileNames);
        });
    });


