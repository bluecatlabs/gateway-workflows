// Copyright 2019 BlueCat Networks. All rights reserved.
// JavaScript for your page goes in here.
$(document).ready(function() {
    //---------------------------On Startup-------------------------
    initialize_form()
    //------------------------Event Listeners-----------------------
    $('input[type=checkbox][name=mac_pool_boolean]').change(function(){
        if($(this).is(':checked')) {
            $('label[for=mac_pool]').show();
            $('#mac_pool').show();
        }
        else {
            $('label[for=mac_pool]').hide();
            $('#mac_pool').hide();
        }
    });

});

function initialize_form() {
    if($('input[type=checkbox][name=mac_pool_boolean]').is(':checked')) {
        $('label[for=mac_pool]').show();
        $('#mac_pool').show();
    }
    else {
        $('label[for=mac_pool]').hide();
        $('#mac_pool').hide();
    }
}
