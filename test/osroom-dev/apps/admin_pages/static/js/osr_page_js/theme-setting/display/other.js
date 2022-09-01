
    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
          media_type:"other",
          medias:[],
          theme_name:"",
          page:1,
          media_view:{},
          media_edit:{},
          media_categorys:[],
          curren_category:"",
          current_theme_name:null,
          theme_names:[],
          start_upload:false,
          checkAll:false, set:false,
          keyword:"",
          img_height:"140px",
          pages:{}
      },
      filters: {
            formatDate: function (time) {
              return irrformatDate(time, "yyyy-MM-dd hh:mm");
            }
      }
    })
    //文件上传配置
    function uploader_conf(data){
        data["theme_name"] = vue.current_theme_name;
        var conf = {
            pick: {
                id: '#filePicker',
                label: '{{_("点击选择文件")}}'
            },
            formData:data,
            fileVal: "upfile",
            dnd: '#dndArea',
            paste: '#uploader',
            swf: '../../dist/Uploader.swf',
            chunked: false,
            chunkSize: 512 * 1024,
            server: "/api/admin/theme/display-setting",
            // 禁掉全局的拖拽功能。这样不会出现图片拖进页面的时候，把图片打开。
            disableGlobalDnd: true,
            fileNumLimit: 30,
            fileSizeLimit:300 * 1024 * 1024,    // 300 M
            fileSingleSizeLimit:30 * 1024 * 1024    // 30 M
        }
        return conf;
    }

