var vue = new Vue({
  el: '#app',
  delimiters:['{[', ']}'],
  data:{
    media:{}
  }
});

// 加载完页面执行
$(document).ready(function(){
    get_media();
});

function get_media(){
    var d = {
        id:$("#id").attr("content"),
    }

    var result = osrHttp("GET","/api/admin/upload/media-file", d, args={not_prompt:true});
    result.then(function (r) {
        vue.media = r.data.media;
    });
}