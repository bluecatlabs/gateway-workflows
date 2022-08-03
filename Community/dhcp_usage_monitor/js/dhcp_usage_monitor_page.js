// Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// By: BlueCat Networks
// Date: 2022-07-10
// Gateway Version: 22.4.1
// Description: DHCP Usage Monitor JS

var reloadInterval = 1000 * 10;
var duColModel = [];
var tpColModel = [];
var time_out = null;

function network2bin (network) {
    const ip = network.split('/')[0];
    const dividedIp = ip.split('.').reverse();
    const byte = 8;

    return dividedIp.reduce((accumulator, v, idx) => {
      const binary = (parseInt(v, 10) << (byte * idx)) >>> 0;
      return accumulator + binary;
    }, 0);
}

function load_col_model() {
    $.ajax({
        type: 'GET',
        url: '/dhcp_usage_monitor/load_col_model',
        async: false
    })
    .done(function(data) {
        duColModel = data.du_nodes
        tpColModel = data.tp_nodes
    })
    .fail(function() {
        alert('Failed to fetch dhcp usages.');
    });
}

function reload_dhcp_usages() {
    $.ajax({
        type: 'GET',
        url: '/dhcp_usage_monitor/load_dhcp_usages',
        async: false
    })
    .done(function(data) {
        var list = $('#dhcp_usage_list');
        for (var i in data) {
            list.setRowData(data[i].id, data[i]);
        }
    })
    .fail(function() {
        alert('Failed to fetch dhcp usages.');
    });
    if ($('#auto_update').prop('checked') == true) {
        time_out = setTimeout('reload_dhcp_usages()', reloadInterval);
    }
}

function get_network_suggestions(req, resp) {
    $.ajax({
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        url: '/dhcp_usage_monitor/get_network_suggestions',
        data: JSON.stringify(req.term),
        dataType: 'json'
    })
    .done(function(data) {
        resp(data);
    })
    .fail(function() {
        alert('Failed to fetch network suggestions.');
    });
}

function update_dhcp_usages() {
    $.ajax({
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        url: '/dhcp_usage_monitor/update_dhcp_usages',
        data: JSON.stringify($('#dhcp_usage_list').getRowData()),
        dataType: 'json'
    });
}

function update_trap_servers() {
    $.ajax({
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        url: '/dhcp_usage_monitor/update_trap_servers',
        data: JSON.stringify($('#trap_server_list').getRowData()),
        dataType: 'json'
    });
}

function get_dhcp_usage(range) {
    var row = null;
    var rows = $('#dhcp_usage_list').getRowData();
    for (var i in rows) {
        if (rows[i].range == range) {
            row = rows[i];
            break;
        }
    }
    return row;
}

function add_dhcp_usage(range, low_watermark, high_watermark) {
    $.ajax({
        type: 'GET',
        url: '/dhcp_usage_monitor/get_dhcp_usage',
        data: {
            range: range,
            low_watermark: low_watermark,
            high_watermark: high_watermark
        },
        dataType: 'json'
    })
    .done(function(data) {
        var list = $('#dhcp_usage_list');
        var row = get_dhcp_usage(range);
        if (row == null) {
            list.addRowData(undefined, data);
        }
        else {
            list.setRowData(row.id, data);
        }
        updated = true;
    })
    .fail(function() {
        alert('Failed to fetch servers.');
    })
}

function is_network_exists(range) {
    var result = false;
    $.ajax({
        type: 'GET',
        url: '/dhcp_usage_monitor/get_network_id',
        data: {
            range: range
        },
        dataType: 'json',
        async: false
    })
    .done(function(data) {
        if (data != 0) {
            result = true;
        }
    })
    .fail(function() {
        alert('Failed to fetch servers.');
    })
    return result;
}

function update_du_list_buttons() {
    var rowId = $('#dhcp_usage_list').getGridParam('selrow');
    $('#delete_du_list').prop('disabled', (rowId == null));
    
    var range = $('#range').val();
    var exists = is_network_exists(range);
    $('#add_du_list').prop('disabled', (range == '' || !exists || get_dhcp_usage(range) != null));
    $('#update_du_list').prop('disabled', (get_dhcp_usage(range) == null));
}

function get_trap_server(ipaddress) {
    var row = null;
    var rows = $('#trap_server_list').getRowData();
    for (var i in rows) {
        if (rows[i].ipaddress == ipaddress) {
            row = rows[i];
            break;
        }
    }
    return row;
}

function add_trap_server(ipaddress, port, snmpver, comstr) {
    var data = {
        ipaddress: ipaddress,
        port: port,
        snmpver: snmpver,
        comstr: comstr
    };
    
    var list = $('#trap_server_list');
    var row = get_trap_server(ipaddress);
    if (row == null) {
        list.addRowData(undefined, data);
    }
    else {
        list.setRowData(ipaddress, data);
    }
}

function update_ts_list_buttons() {
    var rowId = $('#trap_server_list').getGridParam('selrow');
    $('#delete_ts_list').prop('disabled', (rowId == null));
    
    var ipaddress = $('#ipaddress').val();
    var comstr = $('#comstr').val();
    var row = get_trap_server(ipaddress);
    
    $('#add_ts_list').prop('disabled', (ipaddress == '' || row != null || comstr == ''));
    $('#update_ts_list').prop('disabled', (row == null || comstr == ''));
}

function upload(file) {
    var uploadFile = document.getElementById('upload_file');
    var file = uploadFile.files[0];
    
    var reader = new FileReader();
    reader.addEventListener('load', update_range_list, false);
    reader.readAsText(file);

    function update_range_list(event){
        var csv = event.target.result;
        var lines = csv.split("\n");
        
        for (i = 1; i < lines.length ;i++) {
            var columns = lines[i].split(",");
            if (2 < columns.length && '' != columns[0]) {
                if (is_network_exists(columns[0])) {
                    add_dhcp_usage(columns[0], columns[1], columns[2]);
                }
                else {
                    var message = `Block/Network(${columns[0]}) is not exist.`
                    alert(message);
                }
            }
        }
        table.draw(false);
    }
}

$(document).ready(function() {
    $('#submit').prop('disabled', true);
    load_col_model();
    
    var duList = $('#dhcp_usage_list');
    duList.jqGrid({
        url: '/dhcp_usage_monitor/load_dhcp_usages',
        datatype: 'json',
        colModel: duColModel,
        height: 190,
        rowNum: 10000,
        pager : '#pager',
        scroll: true,
        loadonce: true,
        caption: text_resource.label_dulist,
        onSelectRow: function(id) {
            if (id != null){
                var row = duList.getRowData(id);
                $('#range').val(row.range);
                $('#low_watermark').val(row.low_watermark);
                $('#high_watermark').val(row.high_watermark);
            }
            update_du_list_buttons();
        }
    });
    
    var tsList = $('#trap_server_list');
    tsList.jqGrid({
        url: '/dhcp_usage_monitor/load_trap_servers',
        datatype: 'json',
        colModel: tpColModel,
        height: '110',
        rowNum: 10000,
        pager : '#trappage',
        scroll: true,
        loadonce: true,
        caption: text_resource.label_tslist,
        onSelectRow: function(id) {
            if (id != null){
                var row = tsList.getRowData(id);
                $('#ipaddress').val(row.ipaddress);
                $('#port').val(row.port);
                $('#snmpver').val(row.snmpver);
                $('#comstr').val(row.comstr);
            }
            update_ts_list_buttons();
        }
    });
    
    update_du_list_buttons();
    update_ts_list_buttons();
    if ($('#auto_update').prop('checked') == true) {
        time_out = setTimeout('reload_dhcp_usages()', reloadInterval);
    }
    
    $('#myTab a').click(function(e) {
      e.preventDefault();
      $(this).tab('show');
    });
    
    // store the currently selected tab in the hash value
    $('ul.nav-tabs > li > a').on('shown.bs.tab', function(e) {
      var id = $(e.target).attr('href').substr(1);
      window.location.hash = id;
    });
    
    // on load of the page: switch to the currently selected tab
    var hash = window.location.hash;
    $('#myTab a[href="' + hash + '"]').tab('show');
    
    
    $('#auto_update').change(function() {
        var checked = $(this).prop('checked');
        if (checked == true) {
            time_out = setTimeout('reload_dhcp_usages()', reloadInterval);
        }
        else if (time_out != null) {
                clearTimeout(time_out);
            time_out = null;
        }
    });
    
    $('#range').autocomplete({
        source: function(req, resp) {
            get_network_suggestions(req, resp);
        },
        close: function( event, ui ) {
            update_du_list_buttons();
        }
    });
    
    $('#range').keyup(function(e) {
        update_du_list_buttons();
    });
    
    $('#upload_file').on('change', function(event) {
        upload($(this));
        $('#submit').prop('disabled', false);
    });
    
    $('#ipaddress, #comstr').keyup(function(e) {
        update_ts_list_buttons();
    });
    
    $('#add_du_list, #update_du_list').on('click', function(e) {
        var range = $('#range').val();
        var low_watermark = $('#low_watermark').val();
        var high_watermark = $('#high_watermark').val();
        add_dhcp_usage(range, low_watermark, high_watermark);
        $('#dhcp_usage_list').resetSelection();
        update_du_list_buttons();
        $('#submit').prop('disabled', false);
    });
    
    $('#delete_du_list').on('click', function(e) {
        var rowId = $('#dhcp_usage_list').getGridParam('selrow');
        if (rowId != null) {
            $('#dhcp_usage_list').delRowData(rowId);
        }
        update_du_list_buttons();
        $('#submit').prop('disabled', false);
    });
    
    $('#add_ts_list, #update_ts_list').on('click', function(e) {
        var ipaddress = $('#ipaddress').val();
        var port = $('#port').val();
        var snmpver = $('#snmpver option:selected').val();
        var comstr = $('#comstr').val();
        add_trap_server(ipaddress, port, snmpver, comstr);
        update_ts_list_buttons();
        $('#submit').prop('disabled', false);
    });
    
    $('#delete_ts_list').on('click', function(e) {
        var rowId = $('#trap_server_list').getGridParam('selrow');
        if (rowId != null) {
            $('#trap_server_list').delRowData(rowId);
        }
        update_ts_list_buttons();
        $('#submit').prop('disabled', false);
    });
    
    $('#submit').on('click', function(e) {
        update_dhcp_usages();
        update_trap_servers();
    });

    $('#cancel').on('click', function(e) {
        location.reload(true);
    });
});
