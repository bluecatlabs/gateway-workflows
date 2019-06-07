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
// Date: 2019-04-25
// Gateway Version: 18.10.2
// Description: Service Point Watcher JS

var colModel = []

function load_col_model() {
    $.ajax({
        type: 'GET',
        url: '/service_point_watcher/load_col_model',
        async: false
    })
    .done(function(data) {
        for (var i in data) {
            colModel.push(data[i]);
        }
    })
    .fail(function() {
        alert('Failed to fetch servers.');
    })
}

function update_status(id, connection, status) {
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
            break;
        }
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
            update_status(data[i].id, data[i].connection, data[i].status);
        }
    })
    .fail(function() {
        alert('Failed to fetch servers.');
    })

    setTimeout('reload_service_points()', 1000 * 10);
}

$(document).ready(function()
{
    var grid = $('#table');

    load_col_model();

    grid.jqGrid({
        url: '/service_point_watcher/load_service_points',
        datatype: 'json',
        colModel: colModel,
        height: 200,
        rowNum: 10000,
        pager : '#pager',
        scroll: true,
        caption: 'Service Point List'
    });

    setTimeout('reload_service_points()', 1000 * 10);

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

});
