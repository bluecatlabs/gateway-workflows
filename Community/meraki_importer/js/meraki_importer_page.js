// Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates
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
// By: Akira Goto (agoto@bluecatnetworks.com)
// Date: 2020-03-31
// Gateway Version: 20.1.1
// Description: CISCO meraki Importer JS

var clientColModel = []

function load_col_model() {
    $.ajax({
        type: 'GET',
        url: '/meraki_importer/load_col_model',
        async: false
    })
    .done(function(data) {
        for (var i in data) {
            clientColModel.push(data[i]);
        }
    })
    .fail(function() {
        alert('Failed to fetch servers.');
    })
}

function update_config() {
    var config = {}
    config['api_key'] = $('#api_key').val();
    config['org_name'] = $('#org_name').val();
    config['network_name'] = $('#network_name').val();
    config['dashboard_url'] = $('#dashboard_url').val();
    config['include_matches'] = $('#include_matches').prop('checked');
    config['include_ipam_only'] = $('#include_ipam_only').prop('checked');
    
    $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",
        url: '/meraki_importer/update_config',
        data: JSON.stringify(config),
        dataType: "json"
    });
}

function get_clients() {
    var grid = $('#table');

    $.ajax({
        type: "GET",
        url: '/meraki_importer/get_clients',
        async: false
    })
    .done(function(data) {
        if (data.length == 0) {
            alert('Failed to fetch clients.');
        }
        else {
            grid.clearGridData();
            for (var i in data) {
                grid.addRowData(undefined, data[i])
            }
        }
    })
    .fail(function() {
        alert('Failed to fetch clients.');
    })
}

function push_selected_clients() {
    var grid = $('#table');
    var rows = grid.getGridParam("selarrrow");
    
    var client_ids = [];
    if (rows.length > 0) {
        for (var i = 0; i < rows.length; i++) {
            var client = grid.getRowData(rows[i]);
            client_ids.push(client['id']);
        }
    }
    $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",
        url: '/meraki_importer/push_selected_clients',
        data: JSON.stringify(client_ids),
        dataType: "json"
    });
}

function clear_clients() {
    var grid = $('#table');
    grid.clearGridData();
    $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",
        url: '/meraki_importer/clear_clients'
    });
}

$(document).ready(function()
{
    var grid = $('#table');

    load_col_model();

    grid.jqGrid({
        url: '/meraki_importer/load_clients',
        datatype: 'json',
        colModel: clientColModel,
        height: 190,
        rowNum: 10000,
        pager : '#pager',
        scroll: true,
        multiselect: true,
        caption: 'Meraki Client List'
    });
    
    $('#get_clients').on('click', function(e)
    {
        $('body').addClass('waiting');
        clear_clients();
        update_config();
        get_clients();
        $("body").removeClass("waiting");
    });

    $('#submit').on('click', function(e)
    {
        $('body').addClass('waiting');
        push_selected_clients();
        $("body").removeClass("waiting");
    });

    $('#cancel').on('click', function(e) {
        clear_clients();
        location.reload(true);
    });
});

