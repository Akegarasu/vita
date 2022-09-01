
    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
          media_type:"image",
          medias:{},
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
          img_w_h:"?w=0&h=140",
          pages:{},
          sort:"",
          inform:{}
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
                label: '{{_("点击选择图片")}}'
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
            fileNumLimit: 100,
            fileSizeLimit:200 * 1024 * 1024,    // 200 M
            fileSingleSizeLimit:10 * 1024 * 1024    // 10 M
        }
        return conf;
    }

    //初始化图片查看器
    var is_init_viewer = false;
    function init_viewer(id) {
        id = id?id:"galley";
        if(!is_init_viewer){
            var $images = $('#'+id);
            $images.on({}).viewer({
                url: 'data-original',
                interval:1500
            });
            is_init_viewer = true;
        }
        $('#'+id).on({}).viewer('update');
    }


