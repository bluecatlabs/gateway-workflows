// Copyright 2018 BlueCat Networks. All rights reserved.
// JavaScript for your page goes in here.
$(document).ready(function(){
    $('#subnetsearch').prop('disabled', false);
    $('#email_button').prop('disabled', false);

    $('#find_subnets').on('click', function (){
        $('#subnet').children('option').remove();

        if($('#subnetsearch').val().trim() == '')
            return;

        var data = {
            "search_text": $('#subnetsearch').val().trim()
        };

        $('#loading').show();
        $('#subnet').prop("disabled", true);
        $('#subnet').hide();
        $('label[for=subnet]').hide();
        $('#email').hide();
        $('label[for=email]').hide();
        $('#email_button').hide();
        $('#report').hide();

        $.post("/SubnetStatus/get_subnets", data, function(response) {
            var dropdown = $("#subnet");
            response.forEach(function(arrayItem){
                dropdown.append($("<option />").val(arrayItem.network_id).text(arrayItem.display_text));
            });

            $('label[for=subnet]').text('Found ' + dropdown.children('option').length + ' matching subnets');

            display_subnet_stats($("#subnet option:first").val());
        }).fail(function() {
            $('#status').show();
            $('#status').html('There was a problem retrieving the subnets');
        })
    });

    $('#subnet').on('change', function (){
        display_subnet_stats($('#subnet').val());
    });
});

function display_subnet_stats(network_id){
    var data = {
            "subnet_id": network_id
    };
    $.post("/SubnetStatus/get_stats", data, function(response) {

        $('#subnet').prop("disabled", false);
        $('#subnet').show();
        $('label[for=subnet]').show();
        $('#email').show();
        $('label[for=email]').show();
        $('#email_button').show();
        $('#report').html(response.report);
        $('#report').show();

        $('#loading').hide();
    }).fail(function() {
        $('#percent_free').hide();
        $('#total').hide();
        $('#free').hide();
        $('#allocated').hide();
        $('#gateway').hide();
        $('#dhcp').hide();

        $('#status').show();
        $('#status').html('There was a problem retrieving the status of the subnet');
    })
}
