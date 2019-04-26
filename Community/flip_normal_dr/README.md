# Flip Main-DR Servers  
**Bluecat Gateway Version:** 18.10.2 and greater  
**BAM Version:** 9.0.0 and greater  

This workflow will flip the IP addresses of a certain application (servers) from a main site to a disaster recover site while retaining the same FQDN.   
It assumes a disaster recovery (business continuity plan) scenario.    

## Prerequisites
1. **BAM Default Configuration**  
This workflow will be using the default configuration value in `/portal/bluecat_portal/config.py` in BlueCat Gateway container.  To set the default configuration, in BlueCat Gateway, go to Administration > Configurations > General Configuration.  
In General Configuration, select the BAM Settings tab and enter the configuration name under "Default Configuration:" and save.  
![screenshot](img/BAM_default_settings.jpg?raw=true "BAM_default_settings")

2. **UDF**  
This workflow requires the following UDF.  
Add the following UDF to Resource Records > Resource Record object in BAM.  
  - Primary    
  Field Name: Primary    
  Display Name: Primary    
  Type: Text  
  - Secondary  
  Field Name: Secondary  
  Display Name: Secondary  
  Type: Text  
  - State  
  Field Name: State  
  Display Name: State  
  Type: Text  
  Predefined Values: Primary | Secondary  

3. **Tag Groups / Tags**  
This workflow requires the following tag groups / tags.    
  - Make a *BCPGroup* tag group in BAM  
![screenshot](img/DR_BCPGroup.jpg?raw=true "DR_BCPGroup")

  - Make an *Application01* tag in tag group *BCPGroup* in BAM
![screenshot](img/DR_app_tag.jpg?raw=true "DR_app_tag")

4. **Host Records**  
Create host records in zones. These host records will be a part of the application group.  
Make sure to populate the following fields: *Name, IP Address, Primary, Secondary, State*.  
Make sure to populate different IP addresses for the *Primary* and *Secondary* fields. (Make sure the network exists)   
If the *State* field is selected to *Primary*, then the *IP address* field and the *Primary* field should have the same IP address. Vice versa for the *Secondary* field.  
It should look something like this:  
![screenshot](img/DR_Host_Record.jpg?raw=true "DR_Host_Record")

5. **Tag Object**  
Tag the host records to the previously made *Application01* tag.
![screenshot](img/DR_RR_tag.jpg?raw=true "DR_RR_tag")

## Usage  

1. **Specify Application Group**  
From the dropdown menu, specify the application which the IP addresses should be flipped from the primary site to the secondary site (and vice versa).  
In this specific scenario choose *Application01*.  
![screenshot](img/DR_flip1.jpg?raw=true "DR_flip1")  

2. **Check Application Server List and Flip**  
Check that the server list has been correctly populated with the host records which was tagged with *Application01*.  
Check that all servers are in their *Primary* state.  
Click *FLIP*.  
![screenshot](img/DR_flip2.jpg?raw=true "DR_flip2")  
Check the *Succeed* message.  
![screenshot](img/DR_flip3.jpg?raw=true "DR_flip3")  

3. **Check Application Server List for results**  
From the dropdown menu, specify the application group which was just flipped.  
In this specific scenario choose *Application01*.  
Check that the *State* has been changed to *Secondary* and the IP addresses has been changed to the secondary IP address.   
![screenshot](img/DR_flip4.jpg?raw=true "DR_flip4")  

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
- Akira Goto (agoto@bluecatnetworks.com)  
- Ryu Tamura (rtamura@bluecatnetworks.com)   

## License
©2019 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved. This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted. Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.
