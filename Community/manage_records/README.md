Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

By: Chris Meyer (cmeyer@bluecatnetworks.com)
Date: 04-01-2019
Gateway Version: 18.12.1
Description: manage_records contains a suite of REST APIs to manage various types of resource records. There is also an option to manage them via bulk operations. The type of records supported are: A, AAAA, CNAME, TXT, MX, and TLSA
/manage_records/create_record
Submit JSON data to create a record. By default records are NOT deployed. Either the deploy_records API can be called, or you can pass in "deploy" as part of the request JSON data, and it will deploy the record immediately. "ping_check" can be added as a part of the request in the JSON request data to have the workflow conduct a ping check prior to assigning the record.
Please see the Postman Collection for examples of all the calls you can make

/manage_records/delete_record
Submit JSON data to delete a record. By default the deletion will be deployed. Pass in "deploy" as part of the JSON data to prevent the delete of the record

/manage_records/update_record
Submit JSON data to update a particular record. This updates the content(for example, the linked IP address to a host name) and not the name or zone of the record. To modify that you must delete and recreate. By default the changes will NOT be deployed. Either the deploy_records API can be called, or you can pass in "deploy" as part of the request JSON data, and it will deploy the record immediately. "ping_check" can be added as a part of the request in the JSON request data to have the workflow conduct a ping check prior to updating the record.

/manage_records/bulk_process
Submit a csv formatted file to do any of the above processes. Here is the format to submit for the type of record:
    Actions - C,U,D
    A - record_type,action,deploy,name,zone,ip
    AAAA - record_type,action,deploy,name,zone,ip
    CNAME - record_type,action,deploy,name,zone,linked_record
    TXT - record_type,action,deploy,name,zone,text
    MX - record_type,action,deploy,name,zone,linked_record
    TLSA - record_type,action,deploy,name,zone,data

/manage_records/deploy_records
Submit a list of IDs via JSON to deploy the records and anything associated with them. This is done using the selective deploy function

/manage_records/get_record
Submit data to retrieve the information of a record

In the folder is a file called "manage_records.postman.json". This file can be imported in Postman as a Collection. It contains example REST calls. It must be used in a Postman Environment with the "server" variable defined which points to a Gateway server.

Installation Directions: 1. Import Workflow into Gateway
                         2. Navigate to the workflow in Gateway in the "workflows" directory
                         3. Modify the manage_records_config.py file to have the correct default values
                         4. Restart Gateway
Known Errors and Bugs: None