
    var vue = new Vue({
      el: '#app',
      delimiters:['{[', ']}'],
      data:{
            title:"",
            post:null,
            issue_name:"{{_('发布')}}",
            save_name:"{{_('保存')}}",
            tag:"",
            categorys:{},
            category:"",
            tags:[],
            editor_name:"markdown",
            customize_key:null
            }
    })

    var vue2 = new Vue({
      el: '#app-2',
      delimiters:['{[', ']}'],
      data:{
            tags:[]
            }
    })

    // 加载完页面执行
    $(document).ready(function(){

        {% if data.editor %}
            vue.editor_name = "{{data.editor}}";
        {% else %}
            vue.editor_name = "{{current_user.editor}}";
        {% endif %}
        get_post();
        get_categorys();
    })

    function get_post(){

        var url_s = get_url_parameter();
        var post_id = get_obj_value(url_s, "id");
        var status = get_obj_value(url_s, "status")
        if (post_id){
            var status=status;

            d = {
                post_id:post_id,
                status:status
            }

             var result = osrHttp("GET","/api/post", d, args={not_prompt:true});
             result.then(function (r) {
                vue.post = r.data.post;
                vue.title = vue.post.title;
                vue.tags = vue.post.tags;
                vue2.tags = vue.tags;
                vue.category = vue.post.category;

                if(vue.editor_name != vue.post.editor){
                    alert("{{_('抱歉!检查到文本编辑器类型错误(editor),请关闭页面重新打开')}}!.");
                }else if(vue.editor_name == "markdown"){
                    simplemde.value(vue.post.content);
                }else if(vue.editor_name == "rich_text"){
                    editor.txt.html(vue.post.content);
                }
                if (r.data.post.issued){
                    vue.issue_name = "{{_('更新发布')}}";
                    vue.save_name = "{{_('存为草稿')}}";
                }else{
                    vue.save_name = "{{_('更新草稿')}}";
                }
             });
        }

    }

    function get_categorys(){
         var result = osrHttp("GET","/api/content/category", {type:"post", action:"get_category"},
                                args={not_prompt:true});
         result.then(function (r) {
            vue.categorys = r.data.categorys;
         });
    }

    function add_tag(){
        if (vue.tag ){
            if (!vue.tags){
                vue.tags = [];

            }
            vue.tags.push(vue.tag);
            vue.tag = "";
        }
        vue2.tags = vue.tags;
    }

    function del_tag(v){
        if (vue.tags){
            vue.tags.splice($.inArray(v, vue.tags),1);
        }
        vue2.tags = vue.tags;
    }

    //当点击提交按钮,提交用于填入的数据到api
    function save(issue_way){
        formValidate();
        if(vue.editor_name == "markdown"){
            var content = simplemde.value();
            var conetent_text = simplemde.value();

        }else if(vue.editor_name == "rich_text"){
            var content = editor.txt.html();
            var conetent_text = editor.txt.text();
        }
        if (vue.post && vue.post._id){
            post_id = vue.post._id;
        }else{
            post_id = null;
        }
        var d = {
                 content_text:conetent_text,
                 content:content,
                 editor:vue.editor_name,
                 title:vue.title,
                 category:vue.category,
                 tags:JSON.stringify(vue.tags),
                 issue_way:issue_way,
                 id:post_id
        }
        // 提交数据
         var result = osrHttp("POST", "/api/user/post", d);
        result.then(function (r) {
            window.onbeforeunload = null;
            if(issue_way){
                location.href = "/osr-admin/own/user";
            }else{
                location.href = "/osr-admin/own/user?s=draft";
            }
        });

    }

    function switch_category(value){
        vue.category = value;
    }

     window.onbeforeunload=function(){
         return "{{_('确认已保存内容后才离开哦')}}";
    }

