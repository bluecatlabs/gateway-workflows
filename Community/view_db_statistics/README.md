# View Database Statistics
This workflow will list relevant statistics of the BAM (BlueCat Address Manager) Database.   

## Prerequisites
1. **BAM Default Configuration**  
This workflow will be using the default configuration value in `/portal/bluecat_portal/config.py` in BlueCat Gateway container.  To set the default configuration, in BlueCat Gateway, go to Administration > Configurations > General Configuration.  
In General Configuration, select the BAM Settings tab and enter the configuration name under "Default Configuration:" and save.  
![screenshot](img/BAM_default_settings.jpg?raw=true "BAM_default_settings")  


## Usage   

1. **Database Statistics Information**  
The statistics information is the following:  
    - Database Size (in MB)  
    - Registered Entity Count  
    - Registered IPv4 Block Count  
    - Registered IPv4 Network Count  
    - Registered IPv4 Address Count  
    - Registered View Count  
    - Registered Zone Count  
    - Registered Resource Record Count  
    - Registered MAC Address Count  
    - Registered User Count  
    - Registered Group Count  
    - Registered Location Count  

![screenshot](img/db_statistics1.jpg?raw=true "db_statistics1")  

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

3. **Appearance**  
This will make the base html menus a little bit wider.  
    1. Copy all files under the directory `additional/templates` to `/portal/templates` inside the Bluecat Gateway container.



## Credits  
By: Akira Goto (agoto@bluecatnetworks.com)  
Date: 2019-04-25  
Gateway Version: 18.10.2

## License
©2019 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved. This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted. Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.
