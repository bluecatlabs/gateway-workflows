# **Community Get Audit Info Workflow**
This workflow is an example for the new Gateway API (get_audit_logs)

___

### Requirements
**BlueCat Gateway version:** 19.5.1 and greater <br/>
**Address Manager version:** v9.0.0 or greater <br/>
**Address Manager:**  Configuration of the Gateway server IP address in the BAM Administration Console. For more information, refer to the section Adding host access to the database in the Address Manager Administration Guide </br>

___

### Description/Example Usage
This workflow allows you to view audit information based on the time interval selected. For more information on this new API, please see the Gateway Administration Guide. 

___

### Prerequisites

1.  SSH into Address Manager as admin: 

*  Enter the following commands:

    * configure database
    * add access <Gateway Server IP Address>
    * save (**NOTE:**: This will stop and start the Address Manager Database)

3.  Log into gateway and import this workflow

4.  Assign workflow permissions 

___

<!--
### Youtube Tutorial

<a href="http://www.youtube.com/watch?feature=player_embedded&v=YOUTUBE_VIDEO_ID_HERE" target="_blank">
 <img src="http://img.youtube.com/vi/YOUTUBE_VIDEO_ID_HERE/0.jpg" alt="IMAGE ALT TEXT HERE" width="240" height="180" border="10" />
</a>
-->

### Known Errors and Bugs: 

1)  None

___

©2019 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved.
This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted.
Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.