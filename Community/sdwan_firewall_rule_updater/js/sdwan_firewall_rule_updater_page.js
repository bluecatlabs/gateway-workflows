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
// Date: 2019-08-28
// Gateway Version: 19.5.1
// Description: SDWAN Firewall Rule Updater JS

var colModel = []

function load_col_model() {
    $.ajax({
        type: 'GET',
        url: '/sdwan_firewall_rule_updater/load_col_model',
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

function add_row(name, port, protocol)
{
    var row = {
        name: name,
        port: port,
        protocol: protocol,
        hash_value: ''
    };
    $("#table").jqGrid('setGridState','visible');
    $("#table").addRowData(undefined, row);
}

function delete_row(rows)
{
    // BUG: http://www.trirand.com/blog/?page_id=393/bugs/delrowdata-bug-on-grid-with-multiselect
    var len = rows.length;

    for(i = len - 1; i >= 0; i--) {
        $("#table").delRowData(rows[i]);
    }
}

function update_domain_lists() {
    $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",
        url: '/sdwan_firewall_rule_updater/submit_domain_lists',
        data: JSON.stringify($('#table').getRowData()),
        dataType: "json"
    });
}

$(document).ready(function()
{
    var grid = $('#table');

    load_col_model();

    grid.jqGrid({
        url: '/sdwan_firewall_rule_updater/load_domain_lists',
        datatype: 'json',
        colModel: colModel,
        height: 150,
        pager : '#pager',
        scroll: true,
        multiselect: true,
        caption: 'Domain Lists'
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


    $('#add_row').on('click', function(e)
    {
        name = $('#domainlist_name').val();
        port = $('#port').val();
        if (port == '') {
            port = 'Any';
        }
        protocol = $('#protocol option:selected').val();
        add_row(name, port, protocol);
    });

    $('#delete_row').on('click', function(e)
    {
        var rows = $("#table").getGridParam("selarrrow");

        if(rows.length == 0) {
            alert("Please select Row(s) to delete.");
        }
        else {
            delete_row(rows);
        }
    });

    $('#submit').on('click', function(e)
    {
        update_domain_lists();
    });

    $('#execute_now').on('click', function(e)
    {
        update_domain_lists();
    });

    $('#cancel').on('click', function(e) {
        location.reload(true);
    });
});
