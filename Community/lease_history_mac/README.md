# Lease History (MAC Address)  
This workflow will list the lease history of a specific MAC Address.  

## Prerequisites
1. **BAM Default Configuration**  
This workflow will be using the default configuration value in `/portal/bluecat_portal/config.py` in BlueCat Gateway container.  To set the default configuration, in BlueCat Gateway, go to Administration > Configurations > General Configuration.  
In General Configuration, select the BAM Settings tab and enter the configuration name under "Default Configuration:" and save.  
![screenshot](img/BAM_default_settings.jpg?raw=true "BAM_default_settings")

## Usage  

1. **Specify MAC Address and list lease history**  
Enter a specific MAC Address in the search field.  
![screenshot](img/lease_history_mac1.jpg?raw=true "lease_history_mac1")  
Click *Search*.  
The lease history data (*IP Address, Lease Time, Expiry Time, Update Count*) will be shown in the table.  
![screenshot](img/lease_history_mac2.jpg?raw=true "lease_history_mac2")  

---

## Additional  

1. **Language**  
You can switch to a Japanese menu by doing the following.  
    1. Create *ja.txt* in the BlueCat Gateway container.  
    ```
    cd /portal/Administration/create_workflow/text/  
    cp en.txt ja.txt  
    ```  
    2. In the BlueCat Gateway web UI, go to Administration > Configurations > General Configuration.   
    In General Configuration, select the *Customization* tab.  
    Under *Language:* type in `ja` and save.  
    ![screenshot](img/langauge_ja.jpg?raw=true "langauge_ja")  

2. **Appearance**  
This will make the base html menus a little bit wider.  
    1. Copy all files under the directory `additional/templates` to `/portal/templates` inside the Bluecat Gateway container.  

## Credits  
By: Akira Goto (agoto@bluecatnetworks.com)  
Date: 2019-03-14  
Gateway Version: 18.10.2

## License
©2019 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved. This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted. Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.
