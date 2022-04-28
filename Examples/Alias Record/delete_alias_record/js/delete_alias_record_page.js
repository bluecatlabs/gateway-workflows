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
$(document).ready(function() {

});


function populate_alias_record_data() {
        var input = $("#alias_record").val();
        var data = $('#alias_record').closest('form').serialize();
        $.post("/delete_alias_record/get_alias_records", data, function(response) {
            $("body").addClass("waiting");
            if (input != $("#alias_record").val()) {
                return;
            }
            if (response.status == "FAIL" || response.data.length == 0) {
                $("#alias_record").clearDisableAllElementsBelow({
                    clear: false
                });
                $("#alias_record").bootstrapError();
            } else {
                $("#alias_record").bootstrapSuccess();
                $("#name").val(response.data['alias_record_name'])
                $("#linked_record").val(response.data['linked_record_name'] + '.' + response.data['linked_record_zone'])
            }
            $("body").removeClass("waiting");
        })
}
