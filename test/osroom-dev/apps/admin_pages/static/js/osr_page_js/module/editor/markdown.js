	var toolbar = [
	    "preview",
		"bold",
		"italic",
		"strikethrough",
		"heading",
		"heading-smaller",
		"heading-bigger",
		"heading-1",
		"heading-2",
		"heading-3",
		"code",
		"quote",
		"unordered-list",
		"ordered-list",
		"clean-block",
		"link",
		"image",
		"table",
		"horizontal-rule",
		"side-by-side",
		"fullscreen",
		"guide"
	]

	var simplemde = new SimpleMDE({
			toolbar:toolbar,
			autofocus: true,
			autosave: {
				enabled: true,
				uniqueId: "MyID",
				delay: 1000,
			},
			element: document.getElementById("myEditor"),
			renderingConfig: {
				singleLineBreaks: false,
				codeSyntaxHighlighting: true,
			},

		});
	simplemde.value("{{_('当前使用的是MarkDown文本编辑器')}}");

	 function upload_img(){

         //上传文件
        var formData = new FormData();
        var name = $("#upfile").attr("name");
        var paths = $("#upfile")[0].files;
        var len = paths.length;
        if(len > 5){
            alert_msg({msg:"{{_('每次最多上传5张图片')}}", msg_type:"w"});
        }
        for(var j = 0, len=len; j < len && j<5; j++) {
            formData.append(paths[j].name, paths[j]);
        }

        var result = osrHttpUpload("POST","/api/upload/file", formData);
        result.then(function (r) {
            if(r.data.msg_type=="s"){
                simplemde.insertImgUrl(r.data.urls);
            }
        });

    }

	$(function() {
        $('#upfile').on('change', function() {
          var fileNames = '';
          $.each(this.files, function() {
            fileNames += '<span class="badge">' + this.name + '</span> ';
          });
          $('#file-list').html(fileNames);
        });
    });


