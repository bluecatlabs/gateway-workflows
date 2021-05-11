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
// Date: 2019-03-14
// Gateway Version: 20.12.1
// Description: Bulk Register MAC Address JS

// JavaScript for your page goes in here.

function load_from_csv(table, stream) {
    var lines = stream.split("\n");

    for (i = 1; i < lines.length ;i++) {
        var columns = lines[i].split(",");
        if (2 < columns.length) {
            var asset_code = (columns[0]).trim();
            var mac_address = (columns[1]).trim();
            var mac_pool = (columns[2]).trim();
            var comments = (columns[3]).trim();
            console.log('No ' + i + '= ' + asset_code + ', ' + mac_address + ', ' + mac_pool, comments);
            table.row.add([asset_code, mac_address, mac_pool, comments]);
        }
    }
};

$(document).ready(function()
{
    $("#file").prop("disabled", false);

    $('#file').on('change', function(event)
    {
        var uploadFile = document.getElementById('file');
        var file = uploadFile.files[0];

        var reader = new FileReader();
        reader.addEventListener('load', update_mac_list, false);
        reader.readAsText(file);

        function update_mac_list(event){
            var table = $("#mac_address_list").DataTable();
            var stream = event.target.result;
            var fileName = file.name.toUpperCase();

            table.clear();
            if (fileName.endsWith(".CSV")) {
                load_from_csv(table, stream);
            }
            table.draw(false);
        }
        $("#submit").prop("disabled", false);
    });

    $('#submit').on('click', function(event)
    {
        event.preventDefault();
        var data_table = $('#mac_address_list').DataTable();
        var json_data = JSON.stringify(data_table.data().toArray());

        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: '/bulk_register_mac_address/submit_bulk_mac_address_list',
            data: json_data,
            dataType: "json"
        }).complete(function()
        {
            location.href = "/bulk_register_mac_address/bulk_register_mac_address_endpoint";
        });
    });
});
