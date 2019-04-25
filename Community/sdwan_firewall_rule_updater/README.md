# Meraki SDWAN Firewall Rule Updater
This workflow will update the firewall rule on a Meraki SDWAN cloud controller based on BlueCat DNS Edge domain lists.  
The updated rule based on the domain lists will be allowed traffic and routing through the firewall.  
This workflow assumes there is a *"Deny All Traffic"* rule at the end in order for only the rules based on DNS Edge domain lists are allowed through.    

## Prerequisites
1. **BAM Default Configuration**  
This workflow will be using the default configuration value in `/portal/bluecat_portal/config.py` in BlueCat Gateway container.  To set the default configuration, in BlueCat Gateway, go to Administration > Configurations > General Configuration.  
In General Configuration, select the BAM Settings tab and enter the configuration name under "Default Configuration:" and save.  
![screenshot](img/BAM_default_settings.jpg?raw=true "BAM_default_settings")  

2. **Additional Python3 Library**  
This workflow requires the python3 *"apscheduler"* library.  
Install the library using PIP3 inside the BlueCat Gateway container.
```
$pip3 install apscheduler

```  

3. **Additional Python Code**  
This workflow requires addtional python code.  
Copy directories *"dnsedge"* and *"sdwan"* under `additional/` to `/portal/bluecat_portal/customizations/integrations/` inside the BlueCat Gateway container.  


## Usage   

1. **Set DNS Edge Parameters**  
![screenshot](img/sdwan_fw1.jpg?raw=true "sdwan_fw1")   

Select the *DNS Edge* tab and set the following parameters:
    - DNS Edge URL:  
      This URL will be the BlueCat DNS Edge CI.  
      The URL should be in the following format:  
      *"https://api-<Your_Edge_CI_URL>"*


    - User Name:  
      This will be the user name which will be used to login to BlueCat DNS Edge CI.  
      Typically it will be a valid e-mail address.  

    - Password:  
      This will be the password to authenticate the above user name.  

Click *"SAVE"*   

2. **Set Meraki Cloud Controller Parameters**  
![screenshot](img/sdwan_fw3.jpg?raw=true "sdwan_fw3")   

Select the *SDWAN* tab and set the following parameters:  
      - API Key:  
        This will be the api key for a certain user to login to the Meraki cloud controller via API.  
        Make sure that API access is enabled in the Meraki cloud controller web UI and a key is generated before setting this parameter.  

![screenshot](img/sdwan_fw5.jpg?raw=true "sdwan_fw5")  
![screenshot](img/sdwan_fw6.jpg?raw=true "sdwan_fw6")  

      - Organization Name:
        This corresponds to the *NETWORK* name in the Meraki cloud controller web UI.  
        Make sure it is the same name (case sensitive) as in the web UI.  

![screenshot](img/sdwan_fw7.jpg?raw=true "sdwan_fw7")  

      - Template Name:  
        This corresponds to the *TEMPLATES* name in the Meraki cloud controller web UI.  
        Make sure it is the same name (case sensitive) as in the web UI.  

![screenshot](img/sdwan_fw8.jpg?raw=true "sdwan_fw8")  

      - Rule Delimiter Keyword(phrase):  
        The updated firewall rules will be set above this keyword, meaning any rule below this keyword will not be overwritten.  
        Typically a *"Deny All Traffic"* rule will be set here so that only the updated firewall rules based on DNS Edge domain lists will be allowed through.  

![screenshot](img/sdwan_fw9.jpg?raw=true "sdwan_fw9")  

Click *"SAVE"*   

3. **Set Domain Lists**  
![screenshot](img/sdwan_fw2.jpg?raw=true "sdwan_fw2")  

Select the *Domain Lists* tab and set the following parameters:  
      - Domain List Name  
        Type in a domain list to be allowed through the firewall.  
        Make sure that the specified domain list is preregistered in DNS Edge CI.  

      - Ports  
        Type in the port number to be allowed through the firewall.  
        Multiple ports can be specified with a comma, or type in *"Any"* for all ports.  

      - Protocol  
        Choose a protocol to be allowed through the firewall from the dropdown menu.

Click *"ADD"* to add a domain list or *"DELETE"* to delete a domain list from the table.  

      - FQDN check box
        Check the FQDN check box if it is a FQDN specific domain list.  
        This means no wild cards in a domain.  

Click *"SAVE"*  

4. **Set Polling Intervals**  
![screenshot](img/sdwan_fw4.jpg?raw=true "sdwan_fw4")  

Select the *Execution* tab and set polling intervals.  
    - Interval (sec):  
      Specify polling intervals.  

If you wish to manually synchronize type in *"0"* in the interval menu and click *"SYNCHRONIZE NOW"*.  
By clicking *"CLEAR"* the settings will be cleared.  


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
By: Akira Goto (agoto@bluecatnetworks.com)  
Date: 2019-04-25  
Gateway Version: 18.10.2

## License
©2019 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved. This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted. Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.
