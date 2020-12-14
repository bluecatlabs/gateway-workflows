Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

By: Murtaza Haider 
Date: 28-03-2019
Gateway Version: 18.12.1
Description: REST workflow that generates a list of BAM users and their permissions. Output report is in CSV format and
is emailed to Mail Admins. Workflow is meant to be used in conjunction with RunDeck as a report scheduling example.
Installation Directions:
    1. Import workflow via GUI
    2. Apply appropriate permissions to the workflow
    3. Configure mail settings in Gateway
        a. Navigate to Administration > Configurations > External DB/Mail Configuration
        b. Select the Mail tab
        c. Enter the appropriate Mail Server, Mail Port, Mail Default Sender, Mail Admins and protocol
        d. If using an authenticated email server then Navigate to the Credentials tab and enter the appropriate
           Mail Username and Password
        e. Select Launch Mail Services
        f. Click Save
    4. Restart the container
REST Examples:
    *** Call the workflow endpoint ***
    -------------------------------------------------------------------------------------------------------------------------------------
    curl -X GET <gateway_ip>/user_inventory/user_inventory_endpoint -H "Content-Type: application/json" -H "Auth: Basic <token>"
    -------------------------------------------------------------------------------------------------------------------------------------
