// Copyright 2022 BlueCat Networks (USA) Inc. and its affiliates
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
// By: BlueCat Networks Inc.
// Date: 2022-05-01
// Gateway Version: 21.11.2
// Description: Health Telemetry DHCP Statistics Viewer Main Page JS

const interval=5;
const buffer_size = 100

function construct_list(id) {
    var title = '';
    var colModel = [];
    
    $.ajax({
        type: 'GET',
        url: '/dhcp_statistics_viewer/load_col_model',
        async: false
    })
    .done(function(data) {
        title = data.title;
        colModel = data.columns;
    })
    .fail(function() {
        alert('Failed to fetch servers.');
    });
    
    var grid = $('#' + id);
    grid.jqGrid({
        url: '/dhcp_statistics_viewer/load_statistics?start=0&count=' + buffer_size,
        datatype: 'json',
        colModel: colModel,
        height: 216,
        rowNum: 10000,
        pager : '#pager',
        scroll: true,
        caption: title
    });
    return grid;
}

function update_statistics_list() {
    var grid = $('#statistics_list');
    $.ajax({
        type: "GET",
        url: '/dhcp_statistics_viewer/load_statistics',
        data: {
            start: 0,
            count: buffer_size
        },
        async: false,
        cache: false
    })
    .done(function(data) {
        var rowId = grid.getGridParam("selrow");
        var scrollTop = grid.closest(".ui-jqgrid-bdiv").scrollTop();
        grid.clearGridData();
        for (var i in data) {
            grid.addRowData(data[i].id, data[i])
        }
        grid.setSelection(rowId, false);
        grid.closest(".ui-jqgrid-bdiv").scrollTop(scrollTop);
    })
    .fail(function() {
        alert('Failed to fetch activities.');
    })
}

function set_detail(key) {
    var detail_string = ""
    $.ajax({
        type: 'GET',
        url: '/dhcp_statistics_viewer/get_statistics/' + key,
        async: false
    })
    .done(function(data) {
        var data_string = JSON.stringify(data, null, '\t');
        $('#detail').val(data_string)
    })
}

$(document).ready(function() {
    var grid = construct_list('statistics_list');
    grid.setGridParam({
        onSelectRow:function(rowid, status, e) {
            set_detail(rowid);
        }
    });
    
    var refresh = null;
    if ($('#auto_refresh').prop('checked')) {
        setInterval('update_statistics_list()', 1000 * interval);
    }
    
    $('#auto_refresh').change(function() {
        if ($(this).prop('checked')) {
            refresh = setInterval('update_statistics_list()', 1000 * interval);
        }
        else {
            clearInterval(refresh);
        }
    });
    
    $('#refresh').on('click', function(e) {
        update_statistics_list();
    });
    
});