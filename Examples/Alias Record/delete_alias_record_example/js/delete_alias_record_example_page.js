// Copyright 2017 BlueCat Networks. All rights reserved.
// JavaScript for your page goes in here.
$(document).ready(function() {

});


function populate_alias_record_data() {
        var input = $("#alias_record").val();
        var data = $('#alias_record').closest('form').serialize();
        $.post("/delete_alias_record_example/get_alias_records", data, function(response) {
            $("body").addClass("waiting");
            if (input != $("#alias_record").val()) {
                return;
            }
            if (response.status == "FAIL" || response.data.length == 0) {
                $("#alias_record").clearDisableAllElementsBelow({
                    clear: false
                });
                $("#alias_record").bootstrapError();
            } else {
                $("#alias_record").bootstrapSuccess();
                $("#name").val(response.data['alias_record_name'])
                $("#linked_record").val(response.data['linked_record_name'] + '.' + response.data['linked_record_zone'])
            }
            $("body").removeClass("waiting");
        })
}
