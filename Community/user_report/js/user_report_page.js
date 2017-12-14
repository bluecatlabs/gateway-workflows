/*
Copyright 2017 BlueCat Networks (USA) Inc. and its affiliates
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
By: Bill Morton (bmorton@bluecatnetworks.com)
Date: 06-12-2017
Gateway Version: 17.10.1
*/

// Copyright 2017 BlueCat Networks. All rights reserved.
// JavaScript for your page goes in here.

    // could not use UI components for the logic I wanted so enable the props
    $(document).ready(function() {
        $('#usergroups').prop('disabled', true);
        $('#submit').prop('disabled', false);
    });

    // This is called by the typeofuser in the form. If Admin, then they are disabled. If Regular, then enabled.
    function by_groups(){

    if ($('#reporttype').val() == 'BY_GROUPS'){
         $('#usergroups').prop('disabled', false);
         $('#submit').prop('disabled', false);
        }
    else {
    $('#usergroups').prop('disabled', true);
    $('#submit').prop('disabled', false);
        }
    }
