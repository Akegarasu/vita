    //当点击提交按钮,提交用于填入的数据到api
    function save_profile(){
        var reg = new RegExp("-","g");//g,表示全部替换
        var birthday = $('#birthday').val().replace(reg,"");
        if(!birthday){
            birthday = vue.birthday.replace(reg,"");
        }
        d = {
            gender:vue.user_profile.gender,
            homepage:vue.user_profile.homepage,
            info:vue.user_profile.introduction,
            birthday:birthday
        }
        // 提交数据
        var result = osrHttp("PUT", '/api/account/profile', d);
        result.then(function (r) {
            if(r.data.msg_type=="s"){
                get_profile();
            }
        });
    }

    $(function(){

        $.fn.datetimepicker.dates['zh-CN'] = {
                days: ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"],
                daysShort: ["周日", "周一", "周二", "周三", "周四", "周五", "周六", "周日"],
                daysMin:  ["日", "一", "二", "三", "四", "五", "六", "日"],
                months: ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
                monthsShort: ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
                today: "今天",
                suffix: [],
                meridiem: ["上午", "下午"]
        };

        var current_lang = '{{g.site_global.language.current}}';
        if(current_lang=="zh_CN"){
            current_lang = "zh-CN";
        }else{
            current_lang = "EN";
        }
        $("#birthday").datetimepicker(
            {
            todayBtn : true,
             format: 'yyyy-mm-dd',
             weekStart:1,
            initialDate: vue.birthday,
            startDate: "1900-01-01",
            startView:4,
            minView : "month",
            maxView:4,
            todayHighlight:true,
            keyboardNavigation:true,
            language:current_lang,
            autoclose:true
            }
        );
    });
