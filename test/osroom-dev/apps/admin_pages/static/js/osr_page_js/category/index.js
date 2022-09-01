var vue = new Vue({
  el: '#app',
  delimiters:['{[', ']}'],
  data:{
    category_types:[],
    curren_type:null,
    categorys:[],
    new_category:"",
    single_type:false
  },
  methods: {show_btn:show_btn}
})

// 加载完页面执行
$(document).ready(function(){

    var type_v = $("#type").attr("content");
    if(type_v){
        vue.curren_type = [type_v, type_v];
    }
    if(vue.curren_type){
        vue.single_type = true;
    }
    get_category_type();
    get_categorys();
})

function show_btn(id){
    alert(id)
    if( $("#"+id).hasClass("show") ){
        // 执行隐藏
        $("#"+id).hide().removeClass("show");
        // 其他
    }else{
        // 显示
        $("#"+id).show().addClass("show");
    }
}
function get_category_type(){

    var result = osrHttp("GET","/api/content/category",
                        {action:'get_category_type'},
                        args={not_prompt:true});
    result.then(function (r) {
        vue.category_types = r.data.types;
        // types keys
        var keys = get_obj_keys(vue.category_types);
        if(!vue.curren_type){
            vue.curren_type = [keys[0], vue.category_types[keys[0]]];
        }else{
            for(var i in vue.category_types) {
                if(vue.category_types[i] == vue.curren_type[1] ){
                    vue.curren_type[0] = i;
                    break;
                }
            }
        }
    });
}

function get_categorys(){

    var result = osrHttp("GET","/api/admin/content/category",
                        {type:vue.curren_type[1]},
                        args={not_prompt:true});
    result.then(function (r) {
        vue.categorys = r.data.categorys;
    });
}

function switch_type(value){
    vue.curren_type[1] = value;
    for(var i in vue.category_types) {
            if(vue.category_types[i] == vue.curren_type[1] ){
                vue.curren_type[0] = i;
                break;
            }
    }

    get_categorys();
}

function add(){

    var d = {
        name:vue.new_category,
        type:vue.curren_type[1]
    }
    // 提交数据
    var result = osrHttp("POST","/api/admin/content/category", d);
    result.then(function (r) {
        if (r.status=="success" && r.data.msg_type=="s"){
            get_categorys();
            vue.new_category = "";
        }
    });
}

function update(id, name){
    var d = {
             name:name,
             id:id,
             type:vue.curren_type[1]
    }
    // 提交数据
    var result = osrHttp("PUT","/api/admin/content/category", d);
    result.then(function (r) {
        if (r.status=="success" && r.data.msg_type=="s"){
            get_categorys();
        }
    });
}

function del(id){

    var d = {
             ids:JSON.stringify([id])
    }
    // 提交数据
    var result = osrHttp("DELETE","/api/admin/content/category", d);
    result.then(function (r) {
        if (r.status=="success" && r.data.msg_type=="s"){
            get_categorys();
        }
    });
}