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
// By: BlueCat Networks
// Date: 2022-06-09
// Gateway Version: 22.11.2
// Description: Bulk Register DHCP Range JS

$(document).ready(function() {
    $("#file").prop("disabled", false);

    $('#file').on('change', function(event) {
        var uploadFile = document.getElementById('file');
        var file = uploadFile.files[0];

        var reader = new FileReader();
        reader.addEventListener('load', update_range_list, false);
        reader.readAsText(file);

        function update_range_list(event){
            var csv = event.target.result;
            var lines = csv.split("\n");

            var table = $("#dhcp_range_list").DataTable();

            table.clear();
            for (i = 1; i < lines.length ;i++) {
                var columns = lines[i].split(",");
                if (2 < columns.length && '' != columns[1]) {
                    var block = (columns[0]).trim();
                    var pool = (columns[1]).trim();
                    var network = (columns[2]).trim();
                    var gateway = (columns[3]).trim();
                    var tag = (columns[4]).trim();
                    var range = (columns[5]).trim();
                    table.row.add([
                        block, pool, network, gateway, tag, range
                    ]);
                }
            }
            table.draw(false);
        }
        $("#submit").prop("disabled", false);
    });
});
