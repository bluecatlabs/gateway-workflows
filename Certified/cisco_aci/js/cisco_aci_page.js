// Copyright 2020 BlueCat Networks. All rights reserved.

function process_render_options(data) {
    var target = '_all';
    if (data.escapeRender) {
        target = data.escapeRender;
        delete data.escapeRender;
    }
    if (data.columnDefs) {
        data.columnDefs.push({'targets': target, 'render': $.fn.dataTable.render.text()});
    }
    else {
        data.columnDefs = [{'targets': target, 'render': $.fn.dataTable.render.text()}];
    }
    return data
}

function toggle_import_checkboxes(checkbox, tenant_name, column_index) {
    var table = $('#output_table').DataTable();
    table.$('#' + tenant_name + '_import_endpoint_devices').prop('disabled', !checkbox.checked);
    table.$('#' + tenant_name + '_overwrite').prop('disabled', !checkbox.checked);
    get_and_toggle_column_header_checkbox(column_index);
}

function get_and_toggle_column_header_checkbox(column_index) {
    var options = {page: 'current'};
    var column = $('#output_table').DataTable().column(column_index, options);
    toggle_column_header_checkbox(column);
}

function select_all_in_column(column_index) {
    var options = {page: 'current'};
    var data = $('#output_table').DataTable().column(column_index, options).nodes().to$().find(':checkbox');
    data.prop('checked', this.checked).change();
}

var id;

var modal = (function() {
    var method = {};
    var $overlay = $('<div id="overlay"></div>');
    var $modal = $('<div id="modal"></div>');
    var $content = $('<div id="content"></div>');
    var $tenants = $('<div id="tenants"><ul></ul></ul></div>');
    var $progress = $('<div id="progress"></div>');
    var $bar = $('<div id="bar"><span id="percentage"></span></div>');
    var $empty = $('<div class="empty"></div>');
    var $exit  = $('<input class="btn-default" id="exit" type="button" value="x" background-color="transparent">');

    $modal.hide();
    $overlay.hide();

    $progress.append($bar);
    $content.append($exit ,$tenants, $empty, $progress);
    $modal.append($content);
    $('body').append($overlay, $modal);
    method.center = function () {
        var top, left;

        top = Math.max($(window).height() - $modal.outerHeight(), 0) / 2;
        left = Math.max($(window).width() - $modal.outerWidth(), 0) / 2;

        $modal.css({
            top:top + $(window).scrollTop(),
            left:left + $(window).scrollLeft()
        });
    };

    method.open = function () {

        $modal.css({
            width: "35%",
            height: "40%"
        })

        method.center();

        $(window).bind('resize.modal', method.center);

        method.show();

        var width = 0, labels = [];
        id = setInterval(frame, 500);

        function frame() {
            $.get('/cisco_aci/progress', function(return_result) {
                var progress = return_result.progress;
                var messages = return_result.messages;
                Object.keys(messages).forEach(function(key, i) {
                    if (messages[key].startsWith('Error!')) {
                        $("#tenants ul").append('<li class="fail">' + messages[key] + '</li>');
                    } else if (messages[key].startsWith('Imported Tenant:')) {
                        $("#tenants ul").append('<li class="success">' + messages[key] + '</li>');
                    } else if (messages[key].startsWith('Import completed')) {
                        $("#tenants ul").append('<li class="warning">' + messages[key] + '</li>');
                    } else {
                        $("#tenants ul").append('<li>' + messages[key] + '</li>');
                    }
                    $tenants.scrollTop($tenants[0].scrollHeight);
                });

                if (progress >= width) {
                    width = parseFloat(progress);
                }
                $bar.width(width + '%');
                $('#percentage').text(width + '%');

                if (width >= 100.0) {
                    clearInterval(id);
                }
            });

        }
    };

    method.close = function () {
        method.hide();

        $(window).off('click');
        $(window).unbind('resize.modal');

        $bar.width('0%')

        $("#tenants ul").empty();
        $('#done').remove();
        $('#completed').remove();
    };

    method.show = function () {
        $modal.show();
        $overlay.show();
    };

    method.hide = function () {
        $modal.hide();
        $overlay.hide();
    };

    method.finish = function () {
        method.show();
        $content.append('<div id="completed" class="empty"></div>');
        $content.append('<div id="done" class="succeed">Completed!</div>');
    };

    method.error = function (message) {
        method.show();
        $content.append('<div id="completed" class="empty"></div>');
        $content.append("<div id='done' class='error'>"+message+"</div>");
    };
    return method;
}());

function toggle_all_checkboxes(button) {
    var table = $('#output_table').DataTable();
    if ($(button).val() == 'DESELECT ALL') {
        table.columns().header().to$().find('input.table_checkbox:checked').prop('checked', false);
        table.$('input.table_checkbox:checked').each(function(index) {
            $(this).prop('checked', false).change();
        });
        $(button).val('SELECT ALL');
    }
    else {
        table.columns().header().to$().find('input.table_checkbox:checkbox:not(:checked)').prop('checked', true);
        table.$('input.table_checkbox:checkbox:not(:checked)').each(function(index) {
            $(this).prop('checked', true).change();
        });
        $(button).val('DESELECT ALL');
    }
}

function toggle_column_header_checkbox(column) {
    if (column.nodes().to$().find(':checked').size() == column.nodes().to$().find(':checkbox').size()) {
        $(column.header()).find('input.table_checkbox').prop('checked', true);
    }
    else {
        $(column.header()).find('input.table_checkbox').prop('checked', false);
    }
}

function add_checkall_button() {
    var label = $('<label>');
    var br = $('<br>');
    var button = $('<input>', {class: 'btn-default', id: 'check_all_button', name: 'check_all_button', type: 'button',
                               value: 'DESELECT ALL'});
    button.click(function() {
        toggle_all_checkboxes(this);
    });
    label.append(br);
    label.append(button);
    $('#output_table_wrapper div.check_all_button' ).html(label);
}

function add_on_page_change_listener() {
    $('#output_table').on('draw.dt', function () {
        var table = $('#output_table').DataTable();
        var options = {page: 'current'};
        table.columns([1, 2, 3], options).every(function() {
            toggle_column_header_checkbox(this);
        });
    });
}

$(document).ready(function() {
    var importing = false
    var progress_button = document.getElementById('import_tenants');
    $('#import_tenants').click( function () {
        if (importing === false) {
            document.getElementById('import_tenants_message_field').innerHTML = '';
            progress_button.value = 'SHOW PROGRESS'
            importing = true
            var data = $('#output_table').DataTable().$('input').serializeArray();
            data.push({name: 'apic_username', value: $('#apic_username').val()})
            data.push({name: 'apic_password', value: $('#apic_password').val()})
            data.push({name: 'apic_ip', value: $('#apic_ip').val()})
            $.post('/cisco_aci/import_tenants', $.param(data))
                .done(function(response) {
                    if (response["status"] === "FAIL" ){
                        modal.error(response["message"]);
                        clearInterval(id);
                    }
                    else
                    {
                        modal.finish();
                    }
                    importing = false;
                    progress_button.value = 'IMPORT INFRASTRUCTURE'
                })
                .fail(function(response) {
                    modal.error(response.responseJSON["description"]);
                    clearInterval(id);
                    importing = false;
                    progress_button.value = 'IMPORT INFRASTRUCTURE'
                });
            modal.open();
        }
        else {
            modal.show();
        }
    });
    $('#exit').click( function () {

        if (importing === true) {
            modal.hide();
        }
        else {
            modal.close();

        }
    });
});
