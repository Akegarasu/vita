    function add_input_tag(conf_key, index){
        var id = osr_guid();
        html = '<div id="'+id+ '" class="list_dict form-group form-icon form-feedback">'
                +'<input class="form-control osr-input" type="text" placeholder="Value" /></div>';

        $("#list_input"+index).before(html);
    }

    function add_dict_tag(conf_key, index){
        var id = osr_guid();
        html = '<div id="'+id+ '" class="list_dict form-group form-icon form-feedback">'
                +'<input class="form-control osr-input" type="text" placeholder="Key:String" />'
                +'<textarea class="form-control osr-input" style="height:80px;" placeholder="Value:String or Json"  ></textarea></div>'
         $("#dict_input"+index).before(html);
    }

    function remove_tag(id){
         $("#"+id).remove();
    }

