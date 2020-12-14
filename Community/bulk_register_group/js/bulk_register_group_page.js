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
// By: BlueCat Networks
// Date: 2019-03-14
// Gateway Version: 18.10.2
// Description: Bulk Register Group JS

// JavaScript for your page goes in here.

$(document).ready(function()
{
    $("#file").prop("disabled", false);

    $('#file').on('change', function(event)
    {
        var uploadFile = document.getElementById('file');
        var file = uploadFile.files[0];

        var reader = new FileReader();
        reader.addEventListener('load', update_ip_list, false);
        reader.readAsText(file);

        function update_ip_list(event){
            var csv = event.target.result;
            var lines = csv.split("\n");

            var table = $("#group_list").DataTable();

            table.clear();
            for (i = 1; i < lines.length ;i++) {
                var columns = lines[i].split(",");
                if (2 < columns.length && '' != columns[0]) {
                    var group_name = (columns[0]).trim();
                    var division_code = (columns[1]).trim();
                    var comments = (columns[2]).trim();

                    table.row.add([group_name, division_code, comments]);
                }
            }
            table.draw(false);
        }
        $("#submit").prop("disabled", false);
    });

    $('#submit').on('click', function(e)
    {
        e.preventDefault();
        var data_table = $('#group_list').DataTable();
        var json_data = JSON.stringify(data_table.data().toArray());

        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: '/bulk_register_group/submit_bulk_group_list',
            data: json_data,
            dataType: "json"
        }).complete(function()
        {
            location.href = "/bulk_register_group/bulk_register_group_endpoint";
        });
    });
});
