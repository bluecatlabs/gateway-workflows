// Copyright 2017 BlueCat Networks. All rights reserved.

var next_route_id = 0;
var selected_id = -1;

function validate_add()
{
    var network = $("#network-input").val();
    var mask = $("#mask-input").val();
    var via = $("#via-input").val();

    if (!valid_ip4_address(network))
    {
        return "Please enter a valid network address.";
    }

    n = parseInt(mask);

    if (isNaN(n))
    {
        return "Please enter a valid mask.";
    }

    if (n < 0 || n > 31)
    {
        return "Please enter a valid mask.";
    }

    if (!valid_ip4_address(via))
    {
        return "Please enter a valid via address.";
    }

    return "";
}


$(document).ready(function() 
{
    $("#delete").prop('disabled', true);
    $("#add").prop('disabled', true);

    $("#routes").jqGrid({
        datatype: "local",
        height: 250,
        colNames: ['Network', 'Mask', 'Via Address'],
        colModel: [
            {
                name: 'network',
                index: 'network',
                width: 175,
                sorttype: "string"
            },
            {
                name: 'mask',
                index: 'mask',
                width: 78,
                sorttype: "int"
            },
            {
                name: 'via',
                index: 'via',
                width: 175
            }
        ],
        onSelectRow: function(id)
        { 
            selected_id = id;
            $('#network-input').val($("#routes").getRowData(id)['network']);
            $('#mask-input').val($("#routes").getRowData(id)['mask']);
            $('#via-input').val($("#routes").getRowData(id)['via']);
            $("#delete").prop('disabled', false);
            $("#error").html("");
            $("#result").html("");
        } 
    });

    $('#configuration').on('change', function() 
    {
        $("#delete").prop('disabled', true);
        $("#add").prop('disabled', true);
        $("#error").html("");
        $("#result").html("");
        $('#network-input').val("");
        $('#mask-input').val("");
        $('#via-input').val("");

        var configuration_id = $("#configuration").val();

        if (configuration_id == 0)
        {
            $("#server").select2("val", "");
            $("#server").empty();
            $("#server").prop('disabled', true);
            $("#routes").jqGrid('clearGridData');
            $("#routes").prop('disabled', true);
        }
        else
        {
            $("body").toggleClass("wait");
            $.ajax({ url: '/configure_bdds_routes/list-servers/' + configuration_id })
                .done(function(data) 
                {
                    $("#server").empty();
                    $("body").toggleClass("wait");
                    $("#server").append('<option selected="selected" value="0">Please Select</option>');
                    for (var server_id in data)
                    {
                        var name = data[server_id];
                        $("#server").append('<option value="' + server_id + '">' + name + '</option>');
                    }
                    $("#server").prop('disabled', false);
                })
                .fail(function() 
                {
                    $("body").toggleClass("wait");
                    alert("Failed to fetch server list.")
                })
        }
    });

    $('#server').on('change', function() 
    {
        var server_id = $("#server").val();

        $("#error").html("");
        $("#result").html("");
        $('#network-input').val("");
        $('#mask-input').val("");
        $('#via-input').val("");

        if (server_id == null || server_id == 0)
        {
            $("#routes").jqGrid('clearGridData');
            $("#routes").prop('disabled', true);
            $("#delete").prop('disabled', true);
            $("#add").prop('disabled', true);
        }
        else
        {
            next_route_id = 0;
            selected_id = -1;
            $("#delete").prop('disabled', true);
            $("#add").prop('disabled', false);
            $("body").toggleClass("wait");
            $.ajax({ url: '/configure_bdds_routes/list-static-routes/' + server_id })
                .done(function(data) 
                {
                    $("#routes").jqGrid('clearGridData');

                    for (var route_id in data)
                    {
                        var network = data[route_id][0];
                        var mask = data[route_id][1];
                        var via = data[route_id][2];
                        route_id = parseInt(route_id);
                        if (route_id >= next_route_id)
                        {
                            next_route_id = route_id + 1;
                        }
                        $("#routes").addRowData(route_id, { 'network' : network, 'via' : via, 'mask' : mask });
                    }

                    $("body").toggleClass("wait");
                })
                .fail(function() 
                {
                    $("body").toggleClass("wait");
                    alert("Failed to fetch static routes.")
                })
        }
    });

    $('#add').on('click', function() 
    {
        var msg = validate_add();

        if (msg == "")
        {
            var network = $('#network-input').val();
            var mask = $('#mask-input').val();
            var via = $('#via-input').val();
            $("#routes").addRowData(next_route_id, { 'network' : network, 'via' : via, 'mask' : mask });
            next_route_id = next_route_id + 1;
            $("#error").html("");
            $("#result").html("");
        }
        else
        {
            $("#error").html(msg);
            $("#result").html("");
        }
    });

    $('#delete').on('click', function() 
    {
        $("#routes").delRowData(selected_id);
        $("#error").html("");
        $("#result").html("");
    });

    $('#save').on('click', function() 
    {
        var server_id = $("#server").val();
        if (server_id <= 0)
        {
            $("#error").html("No server selected.");
            $("#result").html("");
        }
        else
        {
            $("body").toggleClass("wait");
            $.ajax({
                type: "POST",
                contentType: "application/json; charset=utf-8",
                url: '/configure_bdds_routes/update-static-routes/' + server_id,
                data: JSON.stringify($('#routes').getRowData()),
                dataType: "json",
                success: function(data) 
                {
                    $("body").toggleClass("wait");
                    if (data["result"] == "success")
                    {
                        $("#error").html("");
                        $("#result").html("Server updated.");
                    }
                    else
                    {
                        $("#error").html(data["error"]);
                        $("#result").html("");
                    }
                },
                error: function(msg)
                {
                    $("body").toggleClass("wait");
                    $("#error").html("Server failure: %s" % msg);
                    $("#result").html("");
                }
            });
        }
    });

});
