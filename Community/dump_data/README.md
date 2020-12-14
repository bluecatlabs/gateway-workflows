<!-- Copyright 2020 BlueCat Networks. All rights reserved. -->

©2020 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved. This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted. Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.

Workflow Version: 1.0 <br/>
Project Title: Dump Data <br/>
Author: Chris Meyer <br/>
Date: 12-14-2020 <br/>
BlueCat Gateway Version: 20.6.1 <br/>
BAM / BDDS Version: 9.2 <br/>
Dependencies: None <br/>
Installation Directions: Download and install like any other Community workflow <br/>
Known Errors and Bugs: None <br/>
Description/Example Usage: This workflow can be utilized to download a CSV file of the properties and type of records in all Views of the default Configuration set in Gateway. The information on the type of records returned are: HostRecord, AliasRecord, and GenericRecord(specifically "A" type)". There is also an endpoint which can be executed to get the same data in JSON format: GET <server>/dump_data/get_records <br/>
BAM API methods: getEntities, getEntitiesByName <br/>
Change Log: 1.0 - Submitted initial functionality <br/>