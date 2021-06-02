<!--  Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates
 -*- coding: utf-8 -*-

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

By: BlueCat Networks
Date: 2021-05-01
Gateway Version: 21.5.1
 Description: DHCP Exporter README.md -->  

# DHCP Exporter  
**Bluecat Gateway Version:** 21.5.1 and greater  
**BAM Version:** 9.3.0 and greater  

This workflow will list and export existing Blocks / Networks / DHCP Ranges / DHCP Reserved IP Addresses.   

## Prerequisites
1. **BAM Default Configuration**  
This workflow will be using the default configuration value in `/portal/bluecat_portal/config.py` in BlueCat Gateway container.  To set the default configuration, in BlueCat Gateway, go to Administration > Configurations > General Configuration.  
In General Configuration, select the BAM Settings tab and enter the configuration name under "Default Configuration:" and save.  
![screenshot](img/BAM_default_settings.jpg?raw=true "BAM_default_settings")  


2. **Python3 openpyxl library**  
This workflow requires the python3 openpyxl library.  
Install openpyxl library using PIP3 inside the BlueCat Gateway container.
```
$pip3 install openpyxl

```  

3. **jqGrid**  
This workflow requires jqGrid.  
Download jqGrid from [HERE](http://www.trirand.com/blog/?page_id=6).  
After downloading, extract the following two files: *"ui.jqgrid.css"* and  *"jquery.jqGrid.min.js"*.  
Copy *"ui.jqgrid.css"* and *"jquery.jqGrid.min.js"* under `/portal/static/js/vendor/jqgrid/` inside the Bluecat Gateway container.  
Create a new directory `jqgrid` under `/portal/static/js/vendor/` if none exists.  

## Optional requirements
1. **UDF**  
This workflow uses the following optional UDFs.  
If the following UDFs are not created, the value in the workflow table and in the exported spreadsheets will be blank.  

    Add the following UDF to the `IPv4 Block`, `IPv4 Address Range`, and `IPv4 Network` object in BAM.  
      - Comments  
      Field Name: Comments   
      Display Name: Comments  
      Type: Text    


## Usage   

1. **Expand tree view**  
Expand tree view and inspect data.  
Existing blocks / networks information will be shown here.
![screenshot](img/dhcp_exporter1.jpg?raw=true "network_exporter1")  

2. **Specify block or network and export**  
Specify a block or a network.  
Choose format:  *Excel* or *CSV*.   
Check *Export Network Structure* if you wish to export the network structure alongside the DHCP data.  
Click *DOWNLOAD*  
![screenshot](img/dhcp_exporter2.jpg?raw=true "network_exporter2")  

3. **Exported file**  
Open the exported file.  
Check that the DHCP data within the specified block / network has been exported.  
![screenshot](img/dhcp_exporter3.jpg?raw=true "network_exporter3")  

---

## Additional  

1. **Adding additional UDF columns**  
If you wish to add more UDF columns to the table, you can do so by editing the *config_en.json* file.  
Add data to the *"props"* section of the JSON file for additional UDF columns.  
For example:  
```
{
    "id": "Comments",
    "title": "Comments",
    "width": 40,
    "gwidth": 180
}
```
    *id* corresponds to the Field Name of the UDF's object.  
    *title* corresponds to name of the column for both the BlueCat Gateway web UI and the exported spreadsheet.  
    *width* corresponds to the width of the column when exported to a spreadsheet. Larger numbers mean wider columns.  
    *gwidth* corresponds to the width of the column shown on the BlueCat Gateway web UI. Larger numbers mean wider columns.  

    When the value of *width* is set to *0*, it will completely hide the column from the BlueCat Gateway web UI.  
    When the value of *gwidth* is set to *0*, it will not be exported to the spreadsheet. 

    Make sure the corresponding UDFs exist on BAM prior to adding additional columns.  
    Edit the *config_ja.json* file for Japanese.  

2. **Language**  
You can switch to a Japanese menu by doing the following.  
    1. Create *ja.txt* in the BlueCat Gateway container.  
    ```
    cd /portal/Administration/create_workflow/text/  
    cp en.txt ja.txt  
    ```  
    2. In the BlueCat Gateway Web UI, go to Administration > Configurations > General Configuration.   
    In General Configuration, select the *Customization* tab.  
    Under *Language:* type in `ja` and save.  
    ![screenshot](img/langauge_ja.jpg?raw=true "langauge_ja")  




## Author    
- Akira Goto (agoto@bluecatnetworks.com)  
- Ryu Tamura (rtamura@bluecatnetworks.com)  

## License
©2021 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved. This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted. Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.
