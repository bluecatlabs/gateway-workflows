©2018 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved. This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted. Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.

Workflow Version: 1.0
Project Title: SubnetStatus
Author: BlueCat Networks
Date: 05-08-2018
Gateway Version: 18.6.1
Dependencies: None
Installation Directions: 1. Import Workflow into Gateway
                         2. For email functionality, ensure the email server settings in Gateway are setup
                         3. Restart Gateway
Known Errors and Bugs: None
Description: This workflow allows you to search for a subnet at either the network or block level. It will give you a report of various pieces of information for the requested subnet, chief among that information being the utilization. The user can also enter an email address and the report will be directly emailed to them

/SubnetStatus/run_stats
Submit JSON data(subnet_id, email) to generate report on the request subnet, which can be a network or block. If an email is submitted it will also email the report to the request email.

In the folder is a file called "SubnetStatus.postman.json". This file can be imported in Postman as a Collection. It contains example REST calls. It must be used in a Postman Environment with the "server" variable defined which points to a Gateway server.