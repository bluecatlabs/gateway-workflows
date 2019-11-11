// Copyright 2019 BlueCat Networks. All rights reserved.
// JavaScript for your page goes in here.

$( document ).ready(function() {
    $('input').keyup(function(){
        $('input:enabled:visible:text').each(function(){
            if (this.value === '') {
                $('#submit').attr('disabled', true)
                return false
            } else {
                $('#submit').attr('disabled', false)
            }
        });
    });
});