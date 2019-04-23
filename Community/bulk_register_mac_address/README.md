# Bulk MAC Address Registration
This workflow will add MAC Addresses in bulk from a CSV file.  

## Prerequisites
1. **BAM Default Configuration**  
This workflow will be using the default configuration value in `/portal/bluecat_portal/config.py` in BlueCat Gateway container.  To set the default configuration, in BlueCat Gateway, go to Administration > Configurations > General Configuration.  
In General Configuration, select the BAM Settings tab and enter the configuration name under "Default Configuration:" and save.  
![screenshot](img/BAM_default_settings.jpg?raw=true "BAM_default_settings")  

2. **UDF**  
This workflow requires the following UDF.  
Add the following UDF to MAC Pool Objects > MAC Address object in BAM.  
  - Asset Code  
  Field Name: AssetCode    
  Display Name: Asset Code   
  Type: Text  
  - Employee Code    
  Field Name: EmployeeCode
  Display Name: Employee Code   
  Type: Text  
  - Update Date  
  Field Name: UpdateDate
  Display Name: Update Date  
  Type: Date  

3. **Python3 scp module**  
This workflow requires the python scp module.  
Install scp module using PIP3 inside the BlueCat Gateway container.
```
$pip3 install scp

```

## Usage  

1. **Create a CSV file**  
Create a CSV file which has "Asset Code", "MAC Address", "Employee Code", and "Update Date" data.  
For example:   
```
Asset Code, MAC Address, Employee Code, Update Date
AIP14062009, 74:2B:62:89:CF:5E, EM20153354, 2016/06/23
AIP13112813, F8:0F:41:9A:AB:CF, EM20062464, 2016/06/16
PAS15034264, 28:18:78:FB:68:24, EM19913122, 2016/06/23
AIP13112675, F8:0F:41:9A:A4:DB, EM20003453, 2016/06/23
INV_PC0000078, 32:59:B7:15:CD:BB, EM19863245, 2016/06/16
INV_PC0000078, 30:59:B7:15:CC:BA, EM20103149, 2016/06/16
INV_PC0000112, B6:AE:2B:22:42:D0, EM20093621, 2016/06/21
INV_PC0000112, B4:AE:2B:22:43:D1, EM20174671, 2016/06/21

```
2. **Import CSV file in BlueCat Gateway**  
Click "Choose File" and select the corresponding CSV file.  
The Group List will be populated as below:  
![screenshot](img/Bulk_mac1.jpg?raw=true "Bulk_mac1")  

3. **Add users to BAM**  
Click "REGISTER".  
![screenshot](img/Bulk_mac2.jpg?raw=true "Bulk_mac2")  

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

## Credits  
By: Akira Goto (agoto@bluecatnetworks.com)  
Date: 2019-03-14  
Gateway Version: 18.10.2

## License
©2019 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved. This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted. Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.
