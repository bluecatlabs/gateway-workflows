# Bulk DHCP Range Registration

**Bluecat Gateway Version:** 18.10.2 and greater  
**BAM Version:** 9.0.0 and greater

This workflow will delete MAC addresses in bulk from a CSV file.  
MAC addresses linked to IP addresses will not be deleted.

## Prerequisites

1. **BAM Default Configuration**  
   This workflow will be using the default configuration value in `/portal/bluecat_portal/config.py` in BlueCat Gateway container. To set the default configuration, in BlueCat Gateway, go to Administration > Configurations > General Configuration.  
   In General Configuration, select the BAM Settings tab and enter the configuration name under "Default Configuration:" and save.  
   ![screenshot](img/BAM_default_settings.jpg?raw=true 'BAM_default_settings')

## Usage

1. **Create CSV file**  
   Create a CSV file which has "MAC Address" data.  
   For example:

   ```csv
   MAC Address
   02-00-00-00-26-2A
   02-00-00-00-26-2B
   02-00-00-00-26-2C
   02-00-00-00-26-2D
   02-00-00-00-26-2E
   02-00-00-00-26-2F
   02-00-00-00-26-30
   02-00-00-00-26-31
   02-00-00-00-26-32
   02-00-00-00-26-33
   02-00-00-00-26-34
   02-00-00-00-26-35
   02-00-00-00-26-36
   ```

2. **Import CSV file**  
   Click `Choose File` and select the corresponding CSV file.  
   The _MAC ADDRESS LIST_ will be populated as below:  
   ![screenshot](img/bulk_delete_mac1.jpg 'Bulk_DHCP1')

3. **Delete MAC Addresses**  
   Click `Delete`.  
   ![screenshot](img/bulk_delete_mac2.jpg 'Bulk_DHCP2')  
   MAC addresses which are linked to an IP address will not be deleted and will be shown in the BlueCat Gateway log file such as below.

   ```
   [2022-08-08 12:52:10.719378] [wsgi] MAC Address 02-00-00-00-26-2F is in configuration(tamulab)
   [2022-08-08 12:52:10.756258] [wsgi] MAC Address 02-00-00-00-26-2F has IP Addresses 192.168.0.11 linked. Deletion aborted for this MAC Address
   ```

4. **Check BAM to see results**

---

## Additional

1. **Language**  
   You can switch to a Japanese menu by doing the following.

   - In the BlueCat Gateway web UI, go to Administration > Configurations > General Configuration.  
     In General Configuration, select the _Customization_ tab.  
     Under _Language:_ type in `ja` and save.  
     ![screenshot](img/langauge_ja.jpg?raw=true 'langauge_ja')

## Author

- Akira Goto (agoto@bluecatnetworks.com)
- Ryu Tamura (rtamura@bluecatnetworks.com)

## License

©2022 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved. This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted. Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.
