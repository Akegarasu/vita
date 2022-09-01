// 加载完页面执行
 var url_f = "/theme/view/{{data.theme}}";
$(document).ready(function() {
    Overlay();
});
function Overlay() {
    var docHeight = $('#iframe-div').height(); //获取窗口高度
    var iframeHeight = $("#iframe-div").width();
    if($('#overlay').length<=0){
        $('#iframe-div').append('<div id="overlay"></div>');
        $('#overlay')
          .height(docHeight)
          .width(iframeHeight)
          .css({
               'opacity': 0.1, //透明度
               'position': 'absolute',
               'top': '50px',
               'background-color': '#00a65a',
               'z-index': 99999 //保证这个悬浮层位于其它内容之上
          });
    }else{
        $('#overlay').fadeIn("fast");
    }



}
function Modi() {
    for (var i = 0; i < 5; i++) {
        var is_modifed = setTimeout("ModifA()", 500);
        if(is_modifed){
            break;
        }
    }
}
function ModifA() {
    var all_a = $('#iframe-id').contents().find('a');
    var is_modifed = false;
    $(all_a).each(function () {
        var url = $(this).attr('href');
        var $urlRegular = /^\/theme\/view\/.+/;
        if(url!=undefined && url.substr(0, 1)=="/" && !$urlRegular.test(url)){
            //console.log($(this).attr('href'));
            if(url=="/"){
                $(this).attr('href',url_f+"/index");
            }else{
                $(this).attr('href',url_f+$(this).attr('href'));
            }
            $(this).removeAttr('target');

            is_modifed = true;
        }
    });
    if(is_modifed){
        $('#overlay').fadeOut("fast");
    }
    return is_modifed
}

var div = $('#iframe-id').contents().find("html").height();
var i = 0;
setInterval(function() {
    var divNew = $('#iframe-id').contents().find("html").height();
    if(div != divNew) {
        Overlay();
        Modi();
        div = divNew;
    } else if(i%6==0) {
        Modi();
        div = divNew;
    }
    i += 1;
}, 500);

