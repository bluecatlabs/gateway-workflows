# Register MAC Address  
**Bluecat Gateway Version:** 18.10.2 and greater  
**BAM Version:** 9.0.0 and greater  

This workflow will register a specified MAC address tied to a certain location.  
It assumes a MAC address filtering scenario where the DHCP server will only lease an IP address to a pre-registered MAC address tied to a certain location.  

## Prerequisites
1. **BAM Default Configuration**  
This workflow will be using the default configuration value in `/portal/bluecat_portal/config.py` in BlueCat Gateway container.  To set the default configuration, in BlueCat Gateway, go to Administration > Configurations > General Configuration.  
In General Configuration, select the BAM Settings tab and enter the configuration name under "Default Configuration:" and save.  
![screenshot](img/BAM_default_settings.jpg?raw=true "BAM_default_settings")  

2. **UDF**  
This workflow requires the following UDF.  
Add the following UDF to MAC Pool Objects > MAC Address object in BAM.  
  - Comments    
  Field Name: Comments   
  Display Name: Comments  
  Type: Text  


## Usage   

1. **MAC Address Register**  
![screenshot](img/mac_address_reg1.jpg?raw=true "mac_address_reg1")  

Enter the following information:  
- *Asset Code (Name)*  
Enter an identifiable name for the MAC Address.  
This field is mandatory.   
- *Check Uniqueness for Asset Code (Name)*  
When this option is checked, it will check against duplicate asset code (name) within the same MAC Pool.  
Check this option if you **DO NOT** want duplicate asset code (name) registered within the same MAC Pool.  
This option will only work when a MAC Address is registered to a specific MAC Pool.  
- *MAC Address*  
Enter the MAC Address you wish to register.  
Either separators (Dash or Colon) can be used.  
This field is mandatory.    
- *MAC Pool*  
From the drop down list, select a MAC Pool to be registered to.  
Select "None" if the MAC Address will not belong to a MAC Pool.  
- *Comments*  
Type in any other comments / description if you wish.  
This field is optional.    

Click *SUBMIT*  
![screenshot](img/mac_address_reg2.jpg?raw=true "mac_address_reg2")  
Check that the *MAC Address has been successfully registered.* message shows.  
 

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

## Author    
- Akira Goto (agoto@bluecatnetworks.com)  
- Ryu Tamura (rtamura@bluecatnetworks.com)    

## License
©2020 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved. This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted. Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.
