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
// Date: 2021-06-01
// Gateway Version: 21.5.1
// Description: DHCP Exporter JS

var colModel = [
    {label:'id',name:'id',index:'id',width:100,sortable:false,hidden:true},
    {label:'order',name:'order',index:'order',width:100,sortable:false,hidden:true},
];

function load_col_model() {
    $.ajax({
        type: 'GET',
        url: '/dhcp_exporter/load_col_model',
        async: false,
        cache: false
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



$(document).ready(function() {
    load_col_model();

    var grid = $('#table');

    grid.jqGrid({
        url: '/dhcp_exporter/load_initial_data',
        datatype: 'json',
        colModel: colModel,
        jsonReader: {
            repeatitems: false,
            cell: '',
        },
        height: 'auto',
        rowNum: 10000,
        pager : '#pager',
        caption: 'IP Space',
        treeGrid: true,
        treeGridModel: 'adjacency',
        treedatatype: 'json',
        ExpandColumn: 'range'
    });

    grid.on('jqGridBeforeExpandTreeGridRow', function(event, rowid, record, children) {
        console.log('rowid(%d)', rowid);
        var id = record.id;
        var level = record.level;
        if (0 == children.length) {
            $.ajax({url: '/dhcp_exporter/load_children_data/' + id + '/' + level})
                .done(function(data) {
                    for (var i in data) {
                        grid.jqGrid('addChildNode', data[i].id, id, data[i]);
                    }
                })
                .fail(function() {
                    alert('Failed to fetch servers.');
                })
        }
        return true;
    });
    
    var download = $('#download');
    
    download.click(function() {
        $("body").addClass("waiting");
        var rowid = grid.getGridParam('selrow');
        var format = $('#format option:selected').val()
        var full = $('#full_output').prop('checked')
        if (rowid == null) {
            rowid = 0
        }
        var a = document.createElement('a');
        a.download = 'exported.csv'
        a.href = '/dhcp_exporter/load_file/' + rowid + '/' + format + '/' + (full ? 'full' : 'skip');
        a.click();
        $("body").removeClass("waiting");
    });
});