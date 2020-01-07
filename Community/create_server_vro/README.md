# **Community: Create Server - vRO User Group Content**
This workflow was used in the 2020 User Groups to show creating a hostname and getting the next available IP Address.
___

### Requirements
**BlueCat Gateway version:** 19.8.1 and greater <br/>
**Address Manager version:** v9.0.0 or greater <br/>
**Address Manager:**  Configuration of the Gateway server IP address in the BAM Administration Console. For more information, refer to the section Adding host access to the database in the Address Manager Administration Guide </br>

___

### Description/Example Usage
This Gateway workflow will create a host record and assign the next available IP Address based on the Networks that are linked to the Tag Group:

___

### Workflow Configuration

1.  Create the following in Address Manager:
    * **Tag Group > vRO Configuration** - This is the base tag group. 
    * **Tag > vRO Networks** - This is the tag used to get the networks
    * **Tag Networks** - The networks used to get next available IP


 <p align="center">
  <img width="50%" height="50%" src="img/tagged_networks.png">
</p>

<!--
### Youtube Tutorial

<a href="http://www.youtube.com/watch?feature=player_embedded&v=YOUTUBE_VIDEO_ID_HERE" target="_blank">
 <img src="http://img.youtube.com/vi/YOUTUBE_VIDEO_ID_HERE/0.jpg" alt="IMAGE ALT TEXT HERE" width="240" height="180" border="10" />
</a>
-->

___

### Known Errors and Bugs: 

1)  If you put workflow's in the folder Admin or Administration, the import/backups will not work properly. Please refrain from using these directories.

___

©2019 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved.
This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted.
Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.




vRO Configuration > vRO Networks