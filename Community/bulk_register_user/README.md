# Bulk User Registration  
**Bluecat Gateway Version:** 18.10.2 and greater  
**BAM Version:** 9.0.0 and greater  

This workflow will add users in bulk from a CSV file.  

## Prerequisites
1. **BAM Default Configuration**  
This workflow will be using the default configuration value in `/portal/bluecat_portal/config.py` in BlueCat Gateway container.  To set the default configuration, in BlueCat Gateway, go to Administration > Configurations > General Configuration.  
In General Configuration, select the BAM Settings tab and enter the configuration name under "Default Configuration:" and save.  
![screenshot](img/BAM_default_settings.jpg?raw=true "BAM_default_settings")  

2. **UDF**  
This workflow requires the following UDF.  
Add the following UDF to Admin > Named User object in BAM.  
  - First Name  
  Field Name: FirstName  
  Display Name: First Name  
  Type: Text  
  - Last Name  
  Field Name: LastName   
  Display Name: Last Name    
  Type: Text   

## Usage  

1. **Create a CSV file**  
Create a CSV file which has "User Name", "Password", "E-mail", "Last Name", "First Name", "Previlege" and "Access Type" data.  
For example:   
```
User Name,Password,E-Mail,Last Name,First Name,Previlege (ADMIN|REGULAR) ,Access Type (GUI|API|GUI_AND_API)
EM20153354, default, jpicard@itlab.bcnlab.corp,Picard,Jean-Luc, ADMIN, GUI_AND_API
EM20062464, default, wriker@itlab.bcnlab.corp,Riker,William, REGULAR, GUI
EM19913122, default, bcrusher@itlab.bcnlab.corp,Crusher,Beverly, ADMIN, GUI_AND_API
EM20003453, default, glaforge@itlab.bcnlab.corp,LaForge,Geordi, REGULAR, GUI
EM19863245, default, tyar@itlab.bcnlab.corp,Yar,Tasha, ADMIN, GUI_AND_API
EM20103149, default, dtroi@itlab.bcnlab.corp,Troi,Deanna, ADMIN, GUI_AND_API
EM20093621, default, worf@itlab.bcnlab.corp,SonofMogh,Worf, REGULAR, GUI
EM20174671, default, data@itlab.bcnlab.corp,Soong,Data, REGULAR, GUI
```
2. **Import CSV file in BlueCat Gateway**  
Click "Choose File" and select the corresponding CSV file.  
The Group List will be populated as below:  
![screenshot](img/Bulk_user1.jpg?raw=true "Bulk_user1")  

3. **Add users to BAM**  
Click "REGISTER".  
![screenshot](img/Bulk_user2.jpg?raw=true "Bulk_user2")  

4. **Check BAM to see results**  

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
©2019 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved. This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted. Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.
