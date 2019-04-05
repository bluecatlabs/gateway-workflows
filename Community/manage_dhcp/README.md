Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

By: Chris Meyer (cmeyer@bluecatnetworks.com)
Date: 04-01-2019
Gateway Version: 18.12.1
Description: manage_dhcp contains a suite of REST APIs to manage DHCP. Please see the Postman Collection for examples of all the calls you can make.
/manage_dhcp/create_reservation
Submit JSON data(mac, ip, duid) to create a DHCP reservation. This supports IPv4 and IPv6. A MAC(IPv4) address or duid(IPv6) must be submitted along with the request, depending on the type of IP you're reserving

/manage_dhcp/delete_reservation
Submit JSON data(ip) to delete a reservation. This supports both IPv4 and IPv6. When deleting it will remove everything associated with the record, including host and alias records

/manage_dhcp/create_scope
Submit JSON data(network, size, start, end) to create a DHCP scope within a network. This support both IPv4 and IPv6. Submit network and size for IPv6 and network, start, end for IPv4.

/manage_dhcp/delete_scope
Submit JSON data(id) to remove a DHCP scope from a network. The id to submit is returned when the scope is created

/manage_dhcp/add_option
Submit JSON data(network, option_value) to add the "tftp-server" deployment option to a network. This option is NOT supported on an IPv6 network

/manage_dhcp/reserve_next_available
Submit JSON data(network, host_name, zone, mac_address) to reserve the next available IP address within the submitted network. The resulting IP state is DHCP Reserved.

In the folder is a file called "manage_dhcp.postman.json". This file can be imported in Postman as a Collection. It contains example REST calls. It must be used in a Postman Environment with the "server" variable defined which points to a Gateway server.

Installation Directions: 1. Import Workflow into Gateway
                         2. Navigate to the workflow in Gateway in the "workflows" directory
                         3. Modify the manage_dhcp_config.py file to have the correct default values
                         4. Restart Gateway
Known Errors and Bugs: None