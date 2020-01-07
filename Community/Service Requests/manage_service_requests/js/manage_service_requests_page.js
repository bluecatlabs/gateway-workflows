// Copyright 2020 BlueCat Networks. All rights reserved.
// JavaScript for your page goes in here.
$(document).ready(function() {
//----------------------Presets---------------------------//
    var table = $('#ticket_table').DataTable();
//--------------------Event Listeners---------------------//
    $('#ticket_table').on('click', 'tr', function () {
        var post_data = table.row(this).data();
        window.location = "/manage_service_requests/form/" + post_data[0] + "/" + post_data[1] + "/" + post_data[2]
    });
});
