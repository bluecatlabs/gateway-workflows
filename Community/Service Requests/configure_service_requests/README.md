# **Community ServiceNow Configuration Workflow**
This will let you configure your ServiceNow values instead of manually updating a config file.

___

### Requirements
**BlueCat Gateway version:** 19.5.1 and greater <br/>
**Python 3rd party libraries:**  os, re, sys, importlib</br>

___

### Description/Example Usage
This configure service request  workflow allows you to configure the ServiceNow request and manage requests workflow. 

___

### Prerequisites

1.  ServiceNow URL 

2.  ServiceNow User Name

3.  Encrypt the ServiceNow Password and create a secret file by going to the workflow Administration > Encrypt Password. The path and file used in the screenshot below is:

workflows/Service Requests/configure_service_requests/.secret


<p align="left">
  <img width="50%" height="50%" src="img/encrypt_snow_pwd.png">
</p>


___

### Workflow Configuration

1.  Navigate to the workflow Service Requests > Configure Service Requests and configure:
    * **ServiceNow URL** - This is the IP Address/Hostname for your SNOW instance
    * **ServiceNow User** - This is the user name used to make REST calls
    * **ServiceNow Secret file and path** - This is the path to the encrypted password file


<p align="left">
  <img width="50%" height="50%" src="img/config_reqs.png">
</p>

___


<!--
### Youtube Tutorial

<a href="http://www.youtube.com/watch?feature=player_embedded&v=YOUTUBE_VIDEO_ID_HERE" target="_blank">
 <img src="http://img.youtube.com/vi/YOUTUBE_VIDEO_ID_HERE/0.jpg" alt="IMAGE ALT TEXT HERE" width="240" height="180" border="10" />
</a>
-->

___

### Known Errors and Bugs: 


___

©2019 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved.
This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted.
Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.
