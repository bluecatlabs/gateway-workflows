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
// Date: 04-05-18
// Gateway Version: 18.6.1
// Description: Certified Gateway workflows

// JavaScript for your page goes in here.
let EMPTY_TABLE = {
        "columns": [
            {"title": "Id"},
            {"title": "Name"},
            {"title": "Type"},
            {"title": "Select"},
        ],
        "data": [],
        "columnDefs": [{"width": "10%", "targets": [3]}]
    };
function deployData(){
    let deploy_error_message = $("#search_message_field");
    deploy_error_message.text("");
    let counter = 0;
    $("form").find(":checkbox").each(function(){
        if ($(this).prop('checked')===true){
            counter++;
        }
    });
    if (counter <= 100 && counter > 0)
    {
        let serialized = $("form").serialize();
        $.ajax({
            type:'POST',
            url:'/selective_deployment/deploy_objects',
            data:serialized,
            dataType:'json',
            success: function(data) {
                if (data.status === 'FAIL') {
                    deploy_error_message.append("ERROR: " + data.message).addClass("fail");
                }
                else {
                    updateData(data.data);
                }

            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                call_output_table(EMPTY_TABLE);
                deploy_error_message.append('ERROR: ' + errorThrown + " see logs for details").addClass("fail");
            }
        })
    }
    else
    {
        call_output_table(EMPTY_TABLE);
        deploy_error_message.append('ERROR: You must select between 1 and 100 records').addClass("fail");
    }
}

function updateData(data_param){
    let deploy_error_message = $("#search_message_field");
    $.ajax({
        type:'POST',
        url:'/selective_deployment/update_objects',
        data:data_param,
        dataType:'json',
        success: function(data) {

            if (data.status === 'STARTED' || data.status === 'QUEUED') {

                if (document.getElementById("deploy").disabled === false){
                    call_output_table(data.data)
                }

                document.getElementById("search").disabled = true;
                setTimeout(function() {
                    updateData(data.data)}, 1000);

            }
            else if (data.status === 'FAIL') {
                deploy_error_message.append("ERROR: " + data.message).addClass("fail");
            }
            else {

                document.getElementById("search").disabled = false;
                call_output_table(data.data)
            }
            document.getElementById("deploy").disabled = true;

        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            call_output_table(EMPTY_TABLE);
            deploy_error_message.append("ERROR: " + errorThrown + " see logs for details").addClass("fail");
        }
    })
}




$(document).ready(function()
{
    $('#deploy').click(deployData);

});


