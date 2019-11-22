Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

By: Murtaza Haider (mhaider@bluecatnetworks.com)
Date: 27-03-2019
Gateway Version: 18.12.1
Description: Create an A record via REST API and instantly deploy it.
Installation Directions:
    1. Import workflow via GUI
    2. Apply appropriate permissions to the workflow
    3. Configure general settings in Gateway
        a. Navigate to Administration > Configurations > General Configuration
        b. Enter the appropriate Default Configuration
        c. Click Save
REST Examples:
    *** Call the workflow endpoint ***
    -------------------------------------------------------------------------------------------------------------------------------------
    curl -X POST <gateway_ip>/create_a_record/create_a_record_endpoint
         -H "Content-Type: application/json"
         -H "Auth: Basic <token>"
         -d '{
	            "record_name": "<record_name>",
	            "address": "<record_address>",
	            "parent_zone": "<record_parent_zone>"
            }'
    -------------------------------------------------------------------------------------------------------------------------------------
