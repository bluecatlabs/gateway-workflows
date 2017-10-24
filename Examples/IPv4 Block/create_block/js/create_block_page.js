// Copyright 2017 BlueCat Networks. All rights reserved.

// JavaScript for your page goes in here.
var populated_blocks = {};
var added_blocks = {};

function get_masked_address(input)
{
    var address = input.split("/")[0];
    var address_parts = address.split(".");
    var i;
    for (i = address_parts.length; i > 0; i--)
    {
        if (address_parts[i - 1] != '0')
        {
            break;
        }
    }
    return address_parts.slice(0, i).join('.');
}

function complete_address(input)
{
    var address_parts = input.split('.');

    for (var i = 0; i < address_parts.length; i++)
    {
        if (address_parts[i] == '')
        {
            address_parts[i] = '0';
        }
    }
    for (i = address_parts.length; i < 4; i++)
    {
        address_parts.push('0');
    }
    return address_parts.join('.');
}

function tight_mask_calculator(address)
{
    address = get_masked_address(address);
    var address_parts = address.split('.');
    if (address_parts[address_parts.length - 1] == '')
    {
        var last_part = 0;
    }
    else
    {
        var last_part = parseInt(address_parts[address_parts.length - 1]);
    }
    var result = 0;
    var mask = 8;
    result = last_part % 2;
    last_part = (last_part - result) / 2;
    while (result == 0 && mask > 0)
    {
        mask = mask - 1;
        result = last_part % 2;
        last_part = (last_part - result) / 2;
    }
    return (address_parts.length - 1) * 8 + mask;
}

function block_calculator(address)
{
    var address_array = address.split('.');
    return address_array.length * 8;
}

function validate_submit()
{
    var configuration_id = $("#configuration").val();
    //var parent_id = $("#parent-list").find( '[value~="' + $("#parent").val() + '"]' ).text();

    if (configuration_id == 0)
    {
        return "Please select a configuration.";
    }


    return "";
}

function get_child_blocks(parent_id, mask)
{
    if (!populated_blocks[parent_id])
    {
        $.ajax({ url: '/create_block/search_block_child/' + parent_id })
            .done(function(data)
            {
                populated_blocks[parent_id] = true;
                populate_list(data, mask);
            })
    }

}

function populate_list(data, mask)
{

    var blocks = [];
    var $parent_list = $("#parent-list");
    var $new_list = $("#parent-list").clone();
    var list_changed = false;
    for (var block_id in data)
    {
        if (!added_blocks[block_id])
        {
            var name = data[block_id][0];
            var cidr = data[block_id][1];
            $new_list.append('<option value="' + cidr + '" name="' + block_id + '">' + cidr + '</option>');
            //parent_list.append('<option value="' + name + '" name="' + block_id + '">' + cidr + '</option>');
            blocks.push(block_id);
            added_blocks[block_id] = true;
            list_changed = true;
        }
    }
    if (list_changed)
    {
        $("#parent-list").replaceWith($new_list);
    }
    if (blocks.length < 5)
    {
        for (var index in blocks)
        {
            if (parseInt(data[blocks[index]][1].split('/')[1], 10) < mask)
            {
                get_child_blocks(blocks[index], mask);
            }
        }
    }

}

function validate_partial_address(address)
{
    address = address.split('/')[0];
    var count = 0;
    for (var address_part in address.split('.'))
    {
        if (!(/^[0-9]+$/.test(address_part) && parseInt(address_part) < 255 && parseInt(address_part) >= 0))
        {
            return false;
        }
        count++;
    }
    if (count > 4)
    {
        return false;
    }
    return true;
}

function validate_cidr(input)
{
    address = input.split('/')[0];
    if (input.includes('/'))
    {
        mask = input.split('/')[1];
        if (!/^([1-9]|[12]\d|3[0-2])$/.test(mask))
        {
            return false;
        }
    }
    if (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(address))
    {
        return true;
    } else
    {
        return false;
    }

}
$(document).ready(function()
{
    $('#configuration').on('change', function()
    {
        var configuration_id = $("#configuration").val();

        $('#name').val("");
        $('#network-input').val("");
        $("#parent").empty();


        if (configuration_id == 0)
        {
            $("#parent").prop('disabled', true);
            $("#name").prop('disabled', true);
            $("#network-input").prop('disabled', true);
            $("#mask-input").prop('disabled', true);
            $("#submit").prop('disabled', true);
        } else {
            $("#parent").prop('disabled', false);
            $("#name").prop('disabled', false);
            $("#network-input").prop('disabled', false);
            $("#mask-input").prop('disabled', false);
            $("#submit").prop('disabled', false);

            $("body").toggleClass("wait");

            $.ajax({ url: '/create_block/search_block_child/' + configuration_id })
                .done(function(data)
                {
                    $("body").toggleClass("wait");
                    $("#parent").val("").change();
                    $("#parent-list").empty();
                    added_blocks = {}
                    populated_blocks = {}
                    populate_list(data, 8);
                    $("#parent-list").prop('disabled', false);
                })
                .fail(function()
                {
                    $("body").toggleClass("wait");
                    alert("Failed to fetch block list.")
                })
        }
    });

    $('#network-input').on('keyup', function()
    {
        var input = $('#network-input').val();

        if (input.includes('/'))
        {
            var address_list = input.split('/');
            $("#mask-input").val(block_calculator(address_list[0]));
        }
        else
        {
            $("#mask-input").val(block_calculator(input));
        }
    });

    $('#parent').bind("keyup", function()
    {
        var input = $('#parent').val();
        var id_list = $("#parent-list").find( '[value^="' + input + '"]' ).each(function()
        {
            return $(this).attr("name");
        }).get();
        /*
        if (input.lastIndexOf('.') == input.length - 1 && validate_partial_address(input))
        {

            for ( var index in id_list)
            {
                get_child_blocks($(id_list[index]).find( '[value^="' + complete_address(input) + '"]' ).attr("name"), tight_mask_calculator(input));
            }

        }
        else*/
        if (id_list.length < 10)
        {
            for ( var index in id_list)
            {
                get_child_blocks($(id_list[index]).attr("name"), tight_mask_calculator(input) + 4);
            }
        }

        var input = $('#parent').val();
        input = input.split("/");
        $("#network-input").val(input[0]);
        $("#mask-input").val(block_calculator(input[0]));
    });

    $('#parent').on("change", function()
    {
        var input = $('#parent').val();
        if (!validate_cidr(input))
        {
            input = $("#parent-list").find( '[value~="' + $("#parent").val() + '"]' ).text();
        }
        if (validate_cidr(input))
        {
            var address = input.split("/");
            var address_parts = address[0].split(".");
            var i;
            for (i = address_parts.length; i > 0; i--)
            {
                if (address_parts[i - 1] != '0')
                {
                    break;
                }
            }
            var masked_address = address_parts.slice(0, i).join('.');
            $("#network-input").val(masked_address + '.');
            $("#mask-input").val(block_calculator(masked_address));
        }
    });

    $('#submit').on('click', function()
    {
        var e = validate_submit();
        if (e == "")
        {
            if ($("#parent").val() == '')
            {
                parent_id = configuration_id;
            }
            else
            {
                var parent_id = $("#parent-list").find( '[value~="' + $("#parent").val() + '"]' ).attr("name");
            }
            $("#result").html(parent_id);
            var configuration_id = $("#configuration").val();
            var blockname = $("#name").val();
            var cidr = $("#network-input").val();
            var mask = $('#mask-input').val();

            if (parent_id == null || parent_id == 0)
            {
                parent_id = configuration_id;
            }

            $("body").toggleClass("wait");
            $.ajax({ url: '/create_block/block_page/' + parent_id + '/' + blockname + '/' + cidr + '/' + mask })
                .done(function(data)
                {
                    $("body").toggleClass("wait");
                    if (data["result"] == "succeed")
                    {
                        $("#result").html("Block created.");
                        $("#result").attr("class", "succeed");
                        $('#name').val("");
                        $('#network-input').val("");
                    }
                    else
                    {
                        $("#result").html(data["result"]);
                        $("#result").attr("class", "fail");
                    }
                })
                .fail(function()
                {
                    $("body").toggleClass("wait");
                    $("#result").html("Failed to create block.");
                    $("#result").attr("class", "fail");
                })
        }
        else
        {
            $("#result").html(e);
            $("#result").attr("class", "fail");
        }
    });
});
