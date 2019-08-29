// Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
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
// Date: 2019-08-28
// Gateway Version: 19.5.1
// Description: Service Point Watcher JS

var spColModel = []
var tpColModel = []

function load_col_model() {
    $.ajax({
        type: 'GET',
        url: '/service_point_watcher/load_col_model',
        async: false
    })
    .done(function(data) {
        for (var i in data.sp_nodes) {
            spColModel.push(data.sp_nodes[i]);
        }
        for (var i in data.tp_nodes) {
            tpColModel.push(data.tp_nodes[i]);
        }
    })
    .fail(function() {
        alert('Failed to fetch servers.');
    })
}

function update_status(id, connection, status, pulling_severity) {
    var grid = $('#table');
    var rows = grid.jqGrid("getRowData");

    for (var i = 0; i < rows.length; i++) {
        if (rows[i].id == id) {
            if (rows[i].connection != connection) {
                grid.jqGrid('setCell', id, 'connection', connection);
            }
            if (rows[i].status != status) {
                grid.jqGrid('setCell', id, 'status', status);
            }
            if (rows[i].pulling_severity != pulling_severity) {
                grid.jqGrid('setCell', id, 'pulling_severity', pulling_severity);
            }
            break;
        }
    }
}

function get_service_points() {
    var grid = $('#table');

    $.ajax({
        type: "GET",
        url: '/service_point_watcher/get_service_points',
        async: false
    })
    .done(function(data) {
        grid.clearGridData();
        for (var i in data) {
            grid.addRowData(undefined, data[i])
        }
    })
    .fail(function() {
        alert('Failed to fetch servers.');
    })
}


function delete_service_points(rows)
{
    // BUG: http://www.trirand.com/blog/?page_id=393/bugs/delrowdata-bug-on-grid-with-multiselect
    var len = rows.length;

    for(i = len - 1; i >= 0; i--) {
        $("#table").delRowData(rows[i]);
    }
}

function reload_service_points() {
    $.ajax({
        type: 'GET',
        url: '/service_point_watcher/load_service_points',
        async: false
    })
    .done(function(data) {
        for (var i in data) {
            update_status(
                data[i].id,
                data[i].connection,
                data[i].status,
                data[i].pulling_severity
            );
        }
    })
    .fail(function() {
        alert('Failed to fetch servers.');
    })

    setTimeout('reload_service_points()', 1000 * 10);
}

function update_service_points() {
    $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",
        url: '/service_point_watcher/update_service_points',
        data: JSON.stringify($('#table').getRowData()),
        dataType: "json"
    });
}
function add_row(ipaddress, port, snmpver, comstr)
{
    var row = {
        ipaddress: ipaddress,
        port: port,
        snmpver: snmpver,
        comstr: comstr
    };

    var rows = $("#trapservers").getRowData()
    for (var i in rows) {
        if ((rows[i].ipaddress == ipaddress) && (rows[i].port == port) &&
            (rows[i].snmpver == snmpver) && (rows[i].comstr)){
                return;
        }
    }

    $("#trapservers").jqGrid('setGridState','visible');
    $("#trapservers").addRowData(undefined, row);
}

function delete_row(rows)
{
    // BUG: http://www.trirand.com/blog/?page_id=393/bugs/delrowdata-bug-on-grid-with-multiselect
    var len = rows.length;

    for(i = len - 1; i >= 0; i--) {
        $("#trapservers").delRowData(rows[i]);
    }
}

function update_trap_servers() {
    $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",
        url: '/service_point_watcher/submit_trap_servers',
        data: JSON.stringify($('#trapservers').getRowData()),
        dataType: "json"
    });
}


$(document).ready(function()
{
    var grid = $('#table');

    load_col_model();

    grid.jqGrid({
        url: '/service_point_watcher/load_service_points',
        datatype: 'json',
        colModel: spColModel,
        height: 190,
        rowNum: 10000,
        pager : '#pager',
        scroll: true,
        multiselect: true,
        caption: 'Service Point List'
    });

    var trap_grid = $('#trapservers');

    trap_grid.jqGrid({
        url: '/service_point_watcher/load_trap_servers',
        datatype: 'json',
        colModel: tpColModel,
        height: '110',
        rowNum: 10000,
        pager : '#trappage',
        scroll: true,
        multiselect: true,
        caption: 'SNMP Trap Server List'
    });

    setTimeout('reload_service_points()', 1000 * 10);


    $('#edge_key_file').on('change', function(event)
    {
        var key_file = document.getElementById('edge_key_file');
        var file = key_file.files[0];

        var reader = new FileReader();
        reader.addEventListener('load', update_client_key, false);
        reader.readAsText(file)

        function update_client_key(event){
            var access_key = JSON.parse(event.target.result);
            document.getElementById('edge_client_id').value = access_key.clientId;
            document.getElementById('edge_secret').value = access_key.clientSecret;
        }
    });

    $('#myTab a').click(function(e) {
      e.preventDefault();
      $(this).tab('show');
    });

    // store the currently selected tab in the hash value
    $("ul.nav-tabs > li > a").on("shown.bs.tab", function(e) {
      var id = $(e.target).attr("href").substr(1);
      window.location.hash = id;
    });

    // on load of the page: switch to the currently selected tab
    var hash = window.location.hash;
    $('#myTab a[href="' + hash + '"]').tab('show');

    $('#get_service_points').on('click', function(e)
    {
        get_service_points();
    });

    $('#delete_service_points').on('click', function(e)
    {
        var rows = $("#table").getGridParam("selarrrow");

        if(rows.length == 0) {
            alert("Please select Row(s) to delete.");
        }
        else {
            delete_service_points(rows);
        }
    });

    $('#add_row').on('click', function(e)
    {
        ipaddress = $('#ipaddress').val();
        port = $('#port').val();
        snmpver = $('#snmpver option:selected').val();
        comstr = $('#comstr').val();
        add_row(ipaddress, port, snmpver, comstr);
    });

    $('#delete_row').on('click', function(e)
    {
        var rows = $("#trapservers").getGridParam("selarrrow");

        if(rows.length == 0) {
            alert("Please select Row(s) to delete.");
        }
        else {
            delete_row(rows);
        }
    });

    $('#submit').on('click', function(e)
    {
        update_service_points();
        update_trap_servers();
    });

    $('#cancel').on('click', function(e) {
        location.reload(true);
    });
});
