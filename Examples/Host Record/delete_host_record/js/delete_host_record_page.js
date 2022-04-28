// Copyright 2020-2022 BlueCat Networks (USA) Inc. and its affiliates
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
// Date: 2022-04-28
// Gateway Version: 22.4.1
// Description: Example Gateway workflow

// JavaScript for your page goes in here.

function updateDeployStatus(deploy_token) {
    var deploy_token_json = {"deploy_token":deploy_token};
    $.ajax({
        type:'POST',
        url:'/delete_host_record/get_deploy_status',
        data:deploy_token_json,
        dataType:'json',
        success: function (deploy_status) {
            // display task result when deployment finishes
            if (deploy_status.status === 'FINISHED') {

                // deployment succeeded
                if (deploy_status.data === 'SUCCEEDED') {
                    var status_msg = "<font size='3' color='#76ce66'>Deployment " + deploy_status.data + "</font>";
                }

                // deployment failed
                else if (deploy_status.data === 'FAILED') {
                    var status_msg = "<font size='3' color='red'>Deployment " + deploy_status.data + "</font>";
                }

                // deployment finished with no changes
                else {
                    var status_msg = "<font size='3' color='white'>Deployment " + deploy_status.data + "</font>";
                }
                document.getElementById('deploy_status').innerHTML = status_msg;
            }
            else {
                // display task status (STARTED/QUEUED) while deploying
                var status_msg = "<font size='3' color='yellow'>Deployment " + deploy_status.status + "</font>";
                document.getElementById('deploy_status').innerHTML = status_msg;
                setTimeout (function() {
                    updateDeployStatus(deploy_token);
                }, 1000);
            }
        },
        error: function(err) {
            alert('Fail to update deployment status');
            console.log("AJAX error in request: " + JSON.stringify(err, null, 2));
        }
    })
}

$(document).ready(function() {
    var deploy_token = document.getElementById('status_token').value;
    if(deploy_token !== '') {
        updateDeployStatus(deploy_token);
    }
});