Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

By: Chris Meyer (cmeyer@bluecatnetworks.com)
Date: 03-28-2019
Gateway Version: 18.12.1
Description: The workflows provides the ability to request a host record within Service Now. This is accomplished by reserving the requested IP and then creating a Change Request ticket within ServiceNow. The host record will only be created once the ticket has been approved using the manage_service_requests workflow

In order to utilize this workflow properly you will need to set a few variables in service_request_host_config. You will need to have your ServiceNow instance URL, account, and password ready to be set.