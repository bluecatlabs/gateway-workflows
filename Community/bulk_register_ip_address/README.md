# Bulk IP Address Registration  
**Bluecat Gateway Version:** 18.10.2 and greater  
**BAM Version:** 9.0.0 and greater  

This workflow will assign static IP Addresses in bulk from a CSV file.  

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

## Usage  

1. **Create a CSV file**  
Create a CSV file which has "IP Address", "Host Name", "MAC Address" and "Comments" data.  
For example:   
```
IP Address, Host Name, MAC Address, Comments
192.168.9.2, xxxx, 74:2B:62:89:CF:5E, Application Server
192.168.9.3,,,
192.168.9.4, yyyy,,Business Main Building DB
192.168.9.6, zzzz, 28:18:78:FB:68:24,File Server
```
2. **Import CSV file in BlueCat Gateway**  
Click "Choose File" and select the corresponding CSV file.  
The IP Address List will be populated as below:  
![screenshot](img/Bulk_IP1.jpg?raw=true "Bulk_IP1")  

3. **Assign IP Address to BAM**  
Click "REGISTER".  
![screenshot](img/Bulk_IP2.jpg?raw=true "Bulk_IP2")  

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
