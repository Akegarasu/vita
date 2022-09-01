/*
    图片裁剪函数, 需要引入 cropper.min.js和cropper.min.css
*/

//头像裁剪上传
function avatar_cut_upload(img_id, btn_input_img_id) {

    'use strict';
    // 初始化
    var $image = $('#'+img_id);
    $image.cropper({
        aspectRatio: '1',
        preview: '.am-img-preview',
        zoomOnWheel: false,
    })

    // 上传图片
    var $inputImage = $('#'+btn_input_img_id);
    var URL = window.URL || window.webkitURL;
    var blobURL;

    if (URL) {
        $inputImage.change(function () {
            var files = this.files;
            var file;

            if (files && files.length) {
               file = files[0];

               if (/^image\/\w+$/.test(file.type)) {
                    blobURL = URL.createObjectURL(file);
                    $image.one('built.cropper', function () {

                        // Revoke when load complete
                       URL.revokeObjectURL(blobURL);
                    }).cropper('reset').cropper('replace', blobURL);
                    $inputImage.val('');
                } else {
                    window.alert('Please choose an image file.');
                }
            }

            // Amazi UI 上传文件显示代码
            var fileNames = '';
            $.each(this.files, function() {
                fileNames += '<span class="am-badge">' + this.name + '</span> ';
            });
            $('#file-list').html(fileNames);
        });
    } else {
        $inputImage.prop('disabled', true).parent().addClass('disabled');
    }
    return $image
}