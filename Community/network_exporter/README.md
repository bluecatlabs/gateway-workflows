# Network Exporter  
**Bluecat Gateway Version:** 18.10.2 and greater  
**BAM Version:** 9.0.0 and greater  

This workflow will list and export existing blocks / networks / IP addresses.   

## Prerequisites
1. **BAM Default Configuration**  
This workflow will be using the default configuration value in `/portal/bluecat_portal/config.py` in BlueCat Gateway container.  To set the default configuration, in BlueCat Gateway, go to Administration > Configurations > General Configuration.  
In General Configuration, select the BAM Settings tab and enter the configuration name under "Default Configuration:" and save.  
![screenshot](img/BAM_default_settings.jpg?raw=true "BAM_default_settings")  

2. **UDF**  
This workflow requires the following UDF.  
Add the following UDF to IPv4 Objects > IPv4 Address object in BAM.  
  - Comments  
  Field Name: Comments   
  Display Name: Comments  
  Type: Text  
  - Owner  
  Field Name: Owner
  Display Name: Owner   
  Type: Text  

    Add the following UDF to IPv4 Objects > IPv4 Address Range object in BAM.  
  - Comments  
  Field Name: Comments   
  Display Name: Comments  
  Type: Text  
  - VLAN ID  
  Field Name: VLANID  
  Display Name: VLAN ID    
  Type: Text  

3. **Python3 openpyxl library**  
This workflow requires the python3 openpyxl library.  
Install openpyxl library using PIP3 inside the BlueCat Gateway container.
```
$pip3 install openpyxl

```  

4. **jqGrid**  
This workflow requires jqGrid in the html templates as shown below:  
![screenshot](img/network_exp_html1.jpg?raw=true "network_exp_html1")  
![screenshot](img/network_exp_html2.jpg?raw=true "network_exp_html2")  

    Download jqGrid from [HERE](http://www.trirand.com/blog/?page_id=6).  
    After downloading, extract the following two files: *"ui.jqgrid.css"* and *"jquery.jqGrid.min.js"*.  
    Copy the two files to `/portal/static/js/vendor/jqgrid/` inside the Bluecat Gateway container.  

## Usage   

1. **Expand tree view**  
Expand tree view and inspect data.  
Existing blocks / networks information will be shown here.
![screenshot](img/network_exporter1.jpg?raw=true "network_exporter1")  

2. **Specify block or network and export**  
Specify a block or a network.  
Choose format:  *Excel* or *CSV*.  
Choose contents: *Network Structure*, *IP Address* or *Structure and IP Address*.  
Check *Export unallocated IP Address* if you wish to export unallocated IP addresses.  
Click *DOWNLOAD*  
![screenshot](img/network_exporter2.jpg?raw=true "network_exporter2")  

3. **Exported file**  
Open the exported file.  
Check that the specified block / network data has been exported.  
![screenshot](img/network_exporter3.jpg?raw=true "network_exporter3")  

      Click a network or switch through worksheets to see each IP address data.  
      ![screenshot](img/network_exporter4.jpg?raw=true "network_exporter4")  

---

## Additional  

1. **Adding additional UDF columns**  
If you wish to add more UDF columns to the table, you can do so by editing the *config_en.json* file.  
The *range* section corresponds to blocks and networks.  
      <img src="img/network_exporter5.jpg" width="320px"> 　　

      *id* corresponds to the Field Name of the IPv4 Address Range object.  
      *title* corresponds to name of the column.  
      *width* corresponds to the width of the column when exported to a spreadsheet.  
      *gwidth* corresponds to the width of the column shown on the BlueCat Gateway web UI.  

      Add the above at the end of the *range* section for each column.  
      For example,  

  ```
  {
      "id": "networktest",  
      "title": "network_test",  
      "width": 20,  
      "gwidth": 200  
  },  
  ```   

  The *address* section corresponds to IPv4 addresses.  
  <img src="img/network_exporter6.jpg" width="320px">   

*id* corresponds to the Field Name of the IPv4 Address object.  
      *title* corresponds to the title of the column.  
      *width* corresponds to the width of the column when exported to a spreadsheet.  

Add the above at the end of the *address* section for each column.  
      For example,  
  ```
  {
      "id": "ipv4addrtest",
      "title": "ipv4addr_test",
      "width": 20  
  },
  ```

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

3. **Appearance**  
This will make the base html menus a little bit wider.  
    1. Copy all files under the directory `additional/templates` to `/portal/templates` inside the Bluecat Gateway container.



## Credits  
- Akira Goto (agoto@bluecatnetworks.com)  
- Ryu Tamura (rtamura@bluecatnetworks.com)
Date: 2019-04-25  

## License
©2019 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved. This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted. Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.
