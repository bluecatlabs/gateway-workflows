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
// Date: 03-14-19
// Gateway Version: 18.10.2
// Description: Flip Main-DR Servers JS

// JavaScript for your page goes in here.

$(document).ready(function()
{
    $('#application').on('change', function()
    {
        var application_id = $('#application').val();

        if (application_id != 0)
        {
            $.ajax({ url: '/flip_normal_dr/applications/' + application_id + '/servers'})
                .done(function(data)
                {
                    var table = $("#server_list").DataTable();
                    
                    table.clear();
                    for (var i in data) {
                        var fqdn = data[i]['fqdn'];
                        var state = data[i]['state'];
                        var addresses = data[i]['addresses'];
                        
                        console.log('No ' + i + '= ' + fqdn + ', ' + state + ', ' + addresses);
                        table.row.add([fqdn, state, addresses]);
                    }
                    table.draw();
                })
                .fail(function()
                {
                    alert("Failed to fetch servers.")
                })
        }
        $("#submit").prop("disabled", false);
    });
});
