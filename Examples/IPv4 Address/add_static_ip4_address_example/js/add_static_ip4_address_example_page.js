// Copyright 2017 BlueCat Networks. All rights reserved.
// JavaScript for your page goes in here.
$(document).ready(function() {

});

function reset_hostname() {
    if ($("#zone").val() == '') {
        $("#hostname").val('');
        $("#hostname").attr("disabled", true);
    }
    else {$("#hostname").attr("disabled", false);}
}

function view_changed() {
    $("#hostname").val('');
    $("#hostname").attr("disabled", true);
    $("#zone").val('')
    $("#zone").attr("disabled", true);
}
