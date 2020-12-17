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
// Date: 2020-06-10
// Gateway Version: 20.3.1
// Description: Isolator with Kompira Cloud Sonar Integration JS

var nodeColModel = []

function load_col_model() {
    $.ajax({
        type: 'GET',
        url: '/isolator_with_sonar_integration/load_col_model',
        async: false
    })
    .done(function(data) {
        for (var i in data) {
            nodeColModel.push(data[i]);
        }
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
    
    config['edge_url'] = $('#edge_url').val();
    config['edge_client_id'] = $('#edge_client_id').val();
    config['edge_secret'] = $('#edge_secret').val();
    config['edge_policy_name'] = $('#edge_policy_name').val();
    
    $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",
        url: '/isolator_with_sonar_integration/update_config',
        data: JSON.stringify(config),
        dataType: "json"
    });
}

function get_nodes() {
    var grid = $('#table');

    $.ajax({
        type: "GET",
        url: '/isolator_with_sonar_integration/get_nodes',
        async: false
    })
    .done(function(data) {
        if (data.length == 0) {
            alert('No node are loaded.');
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
        url: '/isolator_with_sonar_integration/push_selected_nodes',
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
        url: '/isolator_with_sonar_integration/clear_nodes'
    });
}

$(document).ready(function()
{
    var grid = $('#table');

    load_col_model();

    grid.jqGrid({
        url: '/isolator_with_sonar_integration/load_nodes',
        datatype: 'json',
        colModel: nodeColModel,
        height: 190,
        rowNum: 10000,
        pager : '#pager',
        scroll: true,
        multiselect: true,
        caption: 'Sonar Node List'
    });
    
    $('#get_nodes').on('click', function(e)
    {
        $('body').addClass('waiting');
        clear_nodes();
        update_config();
        get_nodes();
        $("body").removeClass("waiting");
    });

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

