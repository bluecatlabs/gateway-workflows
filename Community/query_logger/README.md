# Query Logger  
**Bluecat Gateway Version:** 18.10.2 and greater  
**BlueCat DNS Edge Version:** 2018.11 and greater  

This workflow will send DNS query logs from the BlueCat DNS Edge CI (Customer Instance) to a designated Syslog server in a syslog format.   
Only the logs that match DNS Edge policies will be sent.    

## Prerequisites  
1. **Additional Python3 Library**  
This workflow requires the python3 *"arrow"*, *"redis"* and the *"apscheduler"* library.  
Install the libraries using PIP3 inside the BlueCat Gateway container.
```
$pip3 install arrow redis apscheduler

```  

2. **Additional Python Code**  
This workflow requires addtional python code.  
Copy the directory *"dnsedge"* under `additional/` to `/portal/bluecat_portal/customizations/integrations/` inside the BlueCat Gateway container.  


## Usage   

1. **Set Parameters**  
Set the following parameters:  
    - DNS Edge URL:  
      This URL will be the BlueCat DNS Edge CI.  
      The URL should be in the following format:  
      *"https://api-<Your_Edge_CI_URL>"*

    - API Token:  
      This refers to the *"SIEM token"* which the primary administrator receives from DNS Edge.  
      It is written in the initial e-mail from DNS Edge as below:  
      ![screenshot](img/query_logger_siem_token.jpg?raw=true "query_logger_siem_token")  

      If you are not a primary administrator (the administrator with an asterisk) and do not know the SIEM token, please contact the primary administrator of the CI.

    - Syslog Server IP Address:  
      This will be the IP address of the server to send the DNS query logs in a syslog format.  
      Make sure that the specified IP address is reachable from BlueCat Gateway.  

    - Poll Interval (seconds):  
      Enter desired polling intervals.  
      The minimum interval is five seconds.  

![screenshot](img/query_logger1.jpg?raw=true "query_logger1")  

Click *SUBMIT*  
Check that the *Configuration was successfully saved* message appears.  

![screenshot](img/query_logger2.jpg?raw=true "query_logger2")  

Check to see whether logs are being sent to the designated server.  

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

2. **Appearance**  
This will make the base html menus a little bit wider.  
    1. Copy all files under the directory `additional/templates` to `/portal/templates` inside the Bluecat Gateway container.  

## Credits  
- Akira Goto (agoto@bluecatnetworks.com)  
- Ryu Tamura (rtamura@bluecatnetworks.com)
Date: 2019-04-25  

## License
©2019 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved. This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted. Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.
