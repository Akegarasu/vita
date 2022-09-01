
    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
          media_type:"video",
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

    var upload_data = {
        name:"批量上传",
        ctype:vue.media_type,
        batch:1,
        category_name:"默认"
    }

    //文件上传配置
    function uploader_conf(data){
        data["theme_name"] = vue.current_theme_name;
        var conf = {
            pick: {
                id: '#filePicker',
                label: '{{_("点击选择视频")}}'
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
            fileNumLimit: 10,
            fileSizeLimit:4000 * 1024 * 1024,    // 4000 M
            fileSingleSizeLimit:2000 * 1024 * 1024    // 1000 M
        }
        return conf;
    }

