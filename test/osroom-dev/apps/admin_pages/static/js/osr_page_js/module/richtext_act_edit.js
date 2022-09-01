var E = window.wangEditor
    var editor = new E('#editor')
    // 或者 var editor = new E( document.getElementById('#editor') )
    //图片上传配置
    // 配置图片服务器端上传地址
    editor.customConfig.uploadImgServer = '/api/upload/file';
    // 将图片大小限制为 xx M
    editor.customConfig.uploadImgMaxSize = 10 * 1024 * 1024;
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

    var current_lang = '{{g.site_global.language.current}}';
    if(current_lang!="zh_CN"){
                editor.customConfig.lang = {
                    '设置标题': 'Title',
                    '正文': 'p',
                    '链接文字': 'Link text',
                    '链接': 'Link',
                    '上传图片': 'Upload image',
                    '上传': 'Upload',
                    '创建': 'Create',
                    '设置列表': 'Setting list',
                    '有序列表': 'Ordered',
                    '无序列表': 'Unordered',
                    '对齐方式': 'Alignment',
                    '靠左': 'Unordered',
                    '居中': 'Centered',
                    '靠右': 'Right',
                    '表情': 'Expression',
                    '手势': 'Gesture',
                    '插入表格': 'Insert table',
                    '行': 'line',
                    '列的表格': 'Columns',
                    '插入视频': 'Insert video',
                    '插入代码': 'Insert code',
                    '格式如': 'Format',
                    '插入': 'Insert',
                    '编辑图片': 'Edit image',
                    '最大宽度': 'Max width',
                    '删除图片': 'Delete',
                    '背景色': 'Background color',
                    '文字颜色': 'Text color',
            }
    }


    editor.customConfig.zIndex=0;
    editor.create();
    editor.txt.html("<p>" + '{{_("您当前使用的是富文本编辑器")}}' + "</p>");