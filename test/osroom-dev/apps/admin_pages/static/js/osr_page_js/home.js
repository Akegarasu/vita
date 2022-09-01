var vue = new Vue({
  el: '#app',
  delimiters:['{[', ']}'],
  data:{
     datas:{user:{},comment:{},post:{},inform:{},plugin:{},message:{},media:{}}

  },
  filters: {
        formatDate: function (time) {
          return formatDate(time, "yyyy-MM-dd hh:mm:ss");
        }
  }
})


// 加载完页面执行
$(document).ready(function(){
    get_datas();
})

function get_datas(){
    var keys = ["post", "comment", "user", "media", "plugin", "message"];
    d = {
        project:JSON.stringify(keys)
    }

    var r = osrHttp("GET","/api/admin/report/basic", d);
    r.then(function (result) {
        vue.datas = result.data;
        //alert_msg({msg:"{{_('数据有缓存延迟')}}", msg_type:"s"});

        // chart
        var days_7 = [];
        var days_30 = [];
        var days_t = [];
        $.each(["post", "comment", "media", "user"], function(i,k) {
            var value = vue.datas[k];
            if(k=="post" || k=="comment" || k=="user"){
                days_7.push(value["7_total"]);
                days_30.push(value["30_total"]);
                days_t.push(value["total"]);
            }else if(k=="media"){
                days_7.push(value["7_total"]);
                days_30.push(value["30_total"]);
                var total = value.media_audio+value.media_image+value.media_other
                    +value.media_text+value.media_video;
                days_t.push(total);
            }

        });
        var popCanvas = $("#d-data");
        var data = {
            labels: ['{{_("文章")}}','{{_("评论")}}','{{_("多媒体")}}','{{_("用户")}}'],
            datasets: [
                {
                    label: '{{_("7天")}}',
                    fillColor: "rgba(255, 99, 132, 0.6)",
                    strokeColor: "rgba(220,220,220,0.8)",
                    highlightFill: "rgba(220,220,220,0.75)",
                    highlightStroke: "rgba(220,220,220,1)",
                    data: days_7,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.6)','rgba(255, 99, 132, 0.6)',
                        'rgba(255, 99, 132, 0.6)','rgba(255, 99, 132, 0.6)']
                },
                {
                    label: '{{_("30天")}}',
                    fillColor: "rgba(151,187,205,0.5)",
                    strokeColor: "rgba(151,187,205,0.8)",
                    highlightFill: "rgba(151,187,205,0.75)",
                    highlightStroke: "rgba(151,187,205,1)",
                    data: days_30,
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.6)','rgba(54, 162, 235, 0.6)',
                        'rgba(54, 162, 235, 0.6)','rgba(54, 162, 235, 0.6)']
                },
                {
                    label:  '{{_("总数")}}',
                    fillColor: "rgba(151,187,205,0.5)",
                    strokeColor: "rgba(151,187,205,0.8)",
                    highlightFill: "rgba(151,187,205,0.75)",
                    highlightStroke: "rgba(151,187,205,1)",
                    data: days_t,
                    backgroundColor: [
                        'rgba(255, 206, 86, 0.6)','rgba(255, 206, 86, 0.6)',
                        'rgba(255, 206, 86, 0.6)','rgba(255, 206, 86, 0.6)']
                }
            ]
            };
        var barChart = new Chart(popCanvas, {
          type: 'bar',
          data: data
        });
     })


}

function get_inform(){
    $("#more").text("{{_('加载中')}}...");
    d = {
        project:JSON.stringify(["inform"])
    }
    var r = osrHttp("GET","/api/admin/report/basic", d);
    r.then(function (result) {
        vue.$set(vue.datas, "inform", result.data.inform);
        $("#more").hide();
    })
}
