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
// By: Akira Goto (agoto@bluecatnetworks.com)
// Date: 2019-10-30
// Gateway Version: 20.12.1
// Description: Fixpoint Kompira Cloud Sonar Importer JS

var nodeColModel = []
var nodeTitle = ''

function load_col_model() {
    $.ajax({
        type: 'GET',
        url: '/sonar_importer/load_col_model',
        async: false
    })
    .done(function(data) {
        nodeTitle = data.title;
        nodeColModel = data.columns;
    })
    .fail(function() {
        alert('Failed to fetch servers.');
    })
}

function update_config() {
    var config = {}
    config['kompira_url'] = $('#kompira_url').val();
    config['api_token'] = $('#api_token').val();
    config['network_name'] = $('#network_name').val();
    config['include_matches'] = $('#include_matches').prop('checked');
    config['include_ipam_only'] = $('#include_ipam_only').prop('checked');
    
    $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",
        url: '/sonar_importer/update_config',
        data: JSON.stringify(config),
        dataType: "json"
    });
}

function get_nodes() {
    var grid = $('#table');

    $.ajax({
        type: "GET",
        url: '/sonar_importer/get_nodes',
        async: false
    })
    .done(function(data) {
        if (data.length == 0) {
            alert('Failed to fetch nodes.');
        }
        else {
            grid.clearGridData();
            for (var i in data) {
                grid.addRowData(undefined, data[i])
            }
        }
    })
    .fail(function() {
        alert('Failed to fetch nodes.');
    })
}

function push_selected_nodes() {
    var grid = $('#table');
    var rows = grid.getGridParam("selarrrow");
    
    var node_ids = [];
    if (rows.length > 0) {
        for (var i = 0; i < rows.length; i++) {
            var node = grid.getRowData(rows[i]);
            node_ids.push(node['id']);
        }
    }
    $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",
        url: '/sonar_importer/push_selected_nodes',
        data: JSON.stringify(node_ids),
        dataType: "json"
    });
}

function clear_nodes() {
    var grid = $('#table');
    grid.clearGridData();
    $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",
        url: '/sonar_importer/clear_nodes'
    });
}

$(document).ready(function()
{
    var grid = $('#table');

    load_col_model();

    grid.jqGrid({
        url: '/sonar_importer/load_nodes',
        datatype: 'json',
        colModel: nodeColModel,
        height: 200,
        rowNum: 10000,
        pager : '#pager',
        scroll: true,
        multiselect: true,
        caption: nodeTitle
    });
    
    $('#get_nodes').on('click', function(e)
    {
        $('body').addClass('waiting');
        clear_nodes();
        update_config();
        get_nodes();
        $("body").removeClass("waiting");
    });

    $('#submit').on('click', function(e)
    {
        $('body').addClass('waiting');
        push_selected_nodes();
        $("body").removeClass("waiting");
    });

    $('#cancel').on('click', function(e) {
        clear_nodes();
        location.reload(true);
    });
});

