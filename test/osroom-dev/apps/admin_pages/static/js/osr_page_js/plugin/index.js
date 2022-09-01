    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
          keyword:"",
          page:1,
          pages:{},
          plugins:[]
      },
      filters: {
            formatDate: function (time) {
              if(time){
                return formatDate(time, "yyyy-MM-dd hh:mm:ss");
              }
              return "";
            }
      }
    })

    // 加载完页面执行
    $(document).ready(function(){
        var page = $("#page").attr("content");
        vue.page = page?page:vue.page;
        var keyword = $("#keyword").attr("content");
        vue.keyword = keyword?keyword:vue.keyword;
        get_plugins(vue.page,vue.keyword);
    })

    function get_plugins(page, keyword){
        vue.keyword = keyword;
        vue.page = page;
        d = {
            page:page,
            keyword:keyword
        }

        var result = osrHttp("GET","/api/admin/plugin", d, args={not_prompt:true});
        result.then(function (r) {
            vue.plugins = r.data.plugins;
            vue.pages = paging(page_total=vue.plugins.page_total,
                            current_page=vue.plugins.current_page);

        });

        var url = window.location.pathname+"?page="+page;
        if(vue.keyword){
            url = url + "&keyword="+vue.keyword;
        }
        history_state(title=null,url=url);
    }

    function operation_plugin(operation, name){

        if(operation=="delete"){
            d = {
                name:name
            }
            var result = osrHttp("DELETE","/api/admin/plugin", d);

        }else if(operation){
            d = {
                action:operation,
                name:name
            }
            var result = osrHttp("PUT","/api/admin/plugin", d);

        }

        result.then(function (r) {
            if(r.data.msg_type=='s'){
                get_plugins(vue.page, vue.keyword);
            }
        }).catch(function (r) {
           get_plugins(vue.page, vue.keyword);
        });


    }

    function upload_plugin(){
        var formData = new FormData();
        var name = $("#upfile").attr("name");
        formData.append("upfile", $("#upfile")[0].files[0]);

        var result = osrHttpUpload("POST","/api/admin/plugin", formData);
        result.then(function (r) {
            if(r.data.msg_type=="s"){
                get_plugins(vue.page, vue.keyword);
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

