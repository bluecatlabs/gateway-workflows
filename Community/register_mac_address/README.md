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
  - Update Date  
  Field Name: UpdateDate   
  Display Name: Update Date  
  Type: Date  
  - User Names  
  Field Name: UserNames  
  Display Name: User Names    
  Type: Text
  - Asset Code  
  Field Name: AssetCode  
  Display Name: Asset Code    
  Type: Text
  - Employee Code  
  Field Name: EmployeeCode   
  Display Name: Employee Code    
  Type: Text

3. **Network and DHCP Range**  
This workflow requires a predefined network and a DHCP range for DHCP lease.  
Create an arbitrarily network and a DHCP range within that network.  

4. **MAC Pool**  
This workflow requires a predefined MAC pool for MAC address registration.  
Create an arbitrarily MAC pool and check *Enable Instant Deployment for changes to this MAC Pool*  
![screenshot](img/mac_address_reg1.jpg?raw=true "mac_address_reg1")  

5. **Tag Groups / Tags**  
This workflow requires the following tag groups / tags.    
  - Make a *Locations* tag group in BAM  
![screenshot](img/mac_address_reg2.jpg?raw=true "mac_address_reg2")  

  - Make an arbitrarily tag in tag group *Locations* in BAM.  

6. **Tag Object**  
Tag the predefined network and MAC pool which was created in 3 and 4 to the tag created in 5.  


## Usage   

1. **MAC Address Register**  
Enter the following information:  
- *MAC Address*  
Type in the MAC address to register.  
- *Device Group*  
Select a device group. Any group will suffice.  
- *Asset Code*  
Type in an arbitrarily asset code of the registering MAC address  
- *Employee Code*  
Type in an arbitrarily employee code of the registering MAC address.  
- *Location*  
Select the location of the registering MAC address.  
The tags created under the tag group *Locations* will appear as a dropdown menu.  
- *Submit Date*  
Specify a submit date. You can either type in a specific date or choose from the calendar.  
- *Expiry Date*  
Specify a expiry date. You can either type in a specific date or choose from the calendar.  

![screenshot](img/mac_address_reg3.jpg?raw=true "mac_address_reg3")  

Click *SUBMIT*  

Check that the *MAC Address has been successfully registered.* message shows.  
![screenshot](img/mac_address_reg4.jpg?raw=true "mac_address_reg4")   

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
