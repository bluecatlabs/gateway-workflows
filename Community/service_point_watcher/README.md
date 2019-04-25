# Service Point Watcher
This workflow will list the DNS Edge Service Points which belongs to a specified CI and show certain information.  
It will only list service points which are associated with an IP address.  


## Prerequisites
1. **BAM Default Configuration**  
This workflow will be using the default configuration value in `/portal/bluecat_portal/config.py` in BlueCat Gateway container.  To set the default configuration, in BlueCat Gateway, go to Administration > Configurations > General Configuration.  
In Genera l Configuration, select the BAM Settings tab and enter the configuration name under "Default Configuration:" and save.  
![screenshot](img/BAM_default_settings.jpg?raw=true "BAM_default_settings")  

2. **Additional Python3 Library**  
This workflow requires the python3 *"apscheduler"* library.  
Install the library using PIP3 inside the BlueCat Gateway container.
```
$pip3 install apscheduler

```  

3. **Additional Python Code**  
This workflow requires addtional python code.  
Copy the directory *"dnsedge"* and under `additional/` to `/portal/bluecat_portal/customizations/integrations/` inside the BlueCat Gateway container.  

4. **jqGrid**  
This workflow requires jqGrid.  
Download jqGrid from [HERE](http://www.trirand.com/blog/?page_id=6).  
After downloading, extract the following two files: *"ui.jqgrid.css"* and *"jquery.jqGrid.min.js"*.  
Copy the two files to `/portal/static/js/vendor/jqgrid/` inside the Bluecat Gateway container.  
Create a *"jqgrid"* directory if it does not exist.   


## Usage   

1. **Set DNS Edge Configurations**  
![screenshot](img/sp_watcher1.jpg?raw=true "sp_watcher1")   

Select the *DNS Edge Configuration* tab and set the following parameters:  
- DNS Edge URL:  
This URL will be the BlueCat DNS Edge CI.  
The URL should be in the following format:  
*"https://api-<Your_Edge_CI_URL>"*  

- User Name:  
This will be the user name which will be used to login to BlueCat DNS Edge CI.  
Typically it will be a valid e-mail address.  

- Password:  
This will be the password to authenticate the above user name.  

- Interval (sec)  
This will set the polling interval to DNS Edge CI.  
If you do not wish to activate Service Point Watcher, specify the interval to *"0"*.

Click *"SAVE"*   
Once saved, Service Point Watcher will be activated and will start to poll to the CI according to the polling intervals.  
If you wish to deactivate Service Point Watcher, specify the interval to *"0"* and save in the *DNS Edge Configuration* tab.  

2. **Service Point List**  
![screenshot](img/sp_watcher2.jpg?raw=true "sp_watcher2")   

All service points which belongs to the specified CI will be listed here.  
Service points which are **NOT** associated with an IP address will not be listed here even if it does belong to the specified CI.  

Information on each column are the following.  
- Name  
The name of the service point.  
It is typically a unique name followed by the first eight digits of the service point ID.   

- IP Address  
The IP address of the service point.  

- Site  
The site which the service point belongs to within the specified CI.  

- Connected  
This shows the connectivity of the service point to the CI.  
A green check mark will be shown if the service point is connected to the CI.  
A green X mark will be shown if the service point is not connected to the CI.  

- Status  
This shows the reachability of the service point from the Service Point Watcher.  
A blue circle will be shown if the service point is reachable from the Service Point Watcher.  
A red circle with a cross will be shown if the service point is unreachable from the Service Point Watcher.  

3. **Service Point Diagnostic API**  
![screenshot](img/sp_watcher3.jpg?raw=true "sp_watcher3")  

If a service point is reachable from the Service Point Watcher, then a service point diagnostic API can be called by clicking the *"Name"* of the service point in the *Service Point List* table.  


---

## Additional   

1. **Language**  
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

2. **Appearance**  
This will make the base html menus a little bit wider.  
    1. Copy all files under the directory `additional/templates` to `/portal/templates` inside the Bluecat Gateway container.



## Credits  
By: Akira Goto (agoto@bluecatnetworks.com)  
Date: 2019-04-25  
Gateway Version: 18.10.2

## License
©2019 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved. This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted. Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.
