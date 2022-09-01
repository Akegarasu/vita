
    $(function(){
        imageObj = avatar_cut_upload(
            img_id="ava-image",
            btn_input_img_id="inputImage"
           )
    });

    function avatar_upload(){
        var data = $("#upload_avatar").data();
        var result = imageObj.cropper(data.method, data.option, data.secondOption);
        switch (data.method) {

            case 'getCroppedCanvas':
            if (result) {

               // 上传头像
               //alert($('#inputImage')[0].files.length)
                var d = {
                    imgfile_base:result.toDataURL('image/png'),

                }

                var result = osrHttp("PUT", "/api/account/upload/avatar", d);
                result.then(function (r) {
                    if(r.data.msg_type=="s"){
                        get_profile();
                    }
                });
            }
            break;
        }

    }

