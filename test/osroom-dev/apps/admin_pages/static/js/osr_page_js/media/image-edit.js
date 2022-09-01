    var media_type = "image";
    $(function() {
        $('#upfile').on('change', function() {
          var fileNames = '';
          $.each(this.files, function() {
            fileNames += '<span class="badge">' + this.name + '</span> ';
          });
          $('#file-list').html(fileNames);
        });
    });

