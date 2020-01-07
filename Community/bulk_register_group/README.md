# Bulk Group Registration  
**Bluecat Gateway Version:** 18.10.2 and greater  
**BAM Version:** 9.0.0 and greater  

This workflow will add user groups in bulk from a CSV file.  

## Prerequisites
1. **BAM Default Configuration**  
This workflow will be using the default configuration value in `/portal/bluecat_portal/config.py` in BlueCat Gateway container.  To set the default configuration, in BlueCat Gateway, go to Administration > Configurations > General Configuration.  
In General Configuration, select the BAM Settings tab and enter the configuration name under "Default Configuration:" and save.  
![screenshot](img/BAM_default_settings.jpg?raw=true "BAM_default_settings")  

2. **UDF**  
This workflow requires the following UDF.  
Add the following UDF to Admin > User Groups object in BAM.  
  - Division Code  
  Field Name: DivisionCode  
  Display Name: Division Code  
  Type: Text  
  - Comments  
  Field Name: Comments  
  Display Name: Comments  
  Type: Text  

## Usage
1. **Create a CSV file**  
Create a CSV file which has "Group Name", "Division Code" and "Comments" data.  
For example:   
```
Group Name,Division Code,Comments
Network Management Grp,DV3098721,IT Mng Div
Server Management Grp,DV3098721,IT Mng Div
Application Management Grp,DV3098733,Dev Div 1
Tokyo DC Management Grp,DV3098225,Tokyo DC Mng Div
```
2. **Import CSV file in BlueCat Gateway**  
Click "Choose File" and select the corresponding CSV file.  
The Group List will be populated as below:  
![screenshot](img/Bulk_group1.jpg?raw=true "Bulk_group1")  

3. **Add user group to BAM**  
Click "REGISTER".  
![screenshot](img/Bulk_group2.jpg?raw=true "Bulk_group2")  

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
©2020 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved. This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted. Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.
