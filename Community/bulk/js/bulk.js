// Copyright 2018 BlueCat Networks. All rights reserved.
// JavaScript for your page goes in here.
$( document ).ready(function() {
    $('#file').on("change", function(){
        if ($('#file').get(0).files.length === 0) {
            $('#submit').prop( "disabled", true );
        } else {
            $('#submit').prop( "disabled", false );
        }
    });
});