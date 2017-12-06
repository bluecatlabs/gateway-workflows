// Copyright 2017 BlueCat Networks. All rights reserved.
// JavaScript for your page goes in here.

    // could not use UI components for the logic I wanted so enable the props
    $(document).ready(function() {
        $('#password').prop('disabled', false);
        $('#submit').prop('disabled', false);
        $('#usergroups').prop('disabled', false);
    });

    // This is called by the typeofuser in the form. If Admin, then they are disabled. If Regular, then enabled.
    function is_admin(){
    $('#password').val();

    if ($('#typeofuser').val() == 'REGULAR'){
         $('#secpriv').prop('disabled', false);
         $('#histpriv').prop('disabled', false);
        }
    else {
    $('#secpriv').prop('disabled', true);
    $('#histpriv').prop('disabled', true);
        }
    }
