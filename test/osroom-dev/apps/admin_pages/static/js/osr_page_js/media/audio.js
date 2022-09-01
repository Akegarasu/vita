
    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
          media_type:"audio",
          medias:[],
          page:1,
          media_view:{},
          media_edit:{},
          media_categorys:[],
          curren_category:"",
          start_upload:false,
          checkAll:false, set:false,
          keyword:"",
          paly_url:"",
          pages:{}
      },
      filters: {
            formatDate: function (time) {
              return irrformatDate(time, "yyyy-MM-dd hh:mm");
            }
      }
    })

    //音频播放
    function play(media){
        vue.paly_url = media.url;
    }

    //文件上传配置
    function uploader_conf(data){

        var conf = {
            pick: {
                id: '#filePicker',
                label: '{{_("点击选择音频")}}'
            },
            formData:data,
            fileVal: "upfile",
            dnd: '#dndArea',
            paste: '#uploader',
            swf: '../../dist/Uploader.swf',
            chunked: false,
            chunkSize: 512 * 1024,
            server: "/api/admin/upload/media-file",
            // 禁掉全局的拖拽功能。这样不会出现图片拖进页面的时候，把图片打开。
            disableGlobalDnd: true,
            fileNumLimit: 100,
            fileSizeLimit:500 * 1024 * 1024,    // 500 M
            fileSingleSizeLimit:100 * 1024 * 1024    // 100 M
        }
        return conf;
    }

