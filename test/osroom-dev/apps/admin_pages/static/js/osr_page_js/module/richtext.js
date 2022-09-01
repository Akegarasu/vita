var E = window.wangEditor
    var editor = new E('#editor')
    // 或者 var editor = new E( document.getElementById('#editor') )
    //图片上传配置
    // 配置图片服务器端上传地址
    editor.customConfig.uploadImgServer = '/api/upload/file';
    // 将图片大小限制为 3M
    editor.customConfig.uploadImgMaxSize = 5 * 1024 * 1024;
    editor.customConfig.uploadImgMaxLength = 5;
    // 将 timeout 时间改为 20 s
    editor.customConfig.uploadImgTimeout = 2000*5;
    editor.customConfig.showLinkImg = false;
    editor.customConfig.uploadFileName = "upfile";
    editor.customConfig.uploadImgHeaders = {
        "X-CSRFToken":csrftoken
    }

    // 其他参数
    editor.customConfig.uploadImgParams = {
        return_url_key: 'data',
        return_state_key:'errno',
        return_success:0,
        return_error:-1,
        zIndex:0,
    }
    //关闭粘贴样式过滤
    editor.customConfig.pasteFilterStyle = false

    // 菜单
    editor.customConfig.menus = [
        'head',  // 标题
        'bold',  // 粗体
        'italic',  // 斜体
        'underline',  // 下划线
        'strikeThrough',  // 删除线
        'foreColor',  // 文字颜色
        'backColor',  // 背景颜色
        'link',  // 插入链接
        'list',  // 列表
        'justify',  // 对齐方式
        'quote',  // 引用
        'emoticon',  // 表情
        'image',  // 插入图片
        'table',  // 表格
        'video',  // 插入视频
        'code',  // 插入代码
        'undo',  // 撤销
        'redo'  // 重复
    ]

    {% include 'module/editor/richtext-tr.html' %}

    editor.customConfig.zIndex=0;
    editor.create();
