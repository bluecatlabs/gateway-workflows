# Absorbaroo
Absorbaroo downloads Office 365 Whitelists and syncs them to DNS Edge and Meraki SDWAN.  
Customers using SDWAN for traffic optimization can leverage this workflow to allow safe traffic to Office 365 sites.  
The following is a typical use case architecture:  

![screenshot](img/absorbaroo_diagram.png?raw=true "absorbaroo_diagram")  


## Prerequisites
1. **BAM Default Configuration**  
This workflow will be using the default configuration value in `/portal/bluecat_portal/config.py` in BlueCat Gateway container.  To set the default configuration, in BlueCat Gateway, go to Administration > Configurations > General Configuration.  
In Genera l Configuration, select the BAM Settings tab and enter the configuration name under "Default Configuration:" and save.  
![screenshot](img/BAM_default_settings.jpg?raw=true "BAM_default_settings")  

2. **Additional Python3 Library**  
This workflow requires the python3 *"apscheduler"* library.  
Install the library using PIP3 inside the BlueCat Gateway container.
```
$pip3 install apscheduler

```  

3. **Additional Python Code**  
This workflow requires addtional python code.  
Copy directories *"dnsedge"*, *"sdwan"* and *"o365"* under `additional/` to `/portal/bluecat_portal/customizations/integrations/` inside the BlueCat Gateway container.  

4. **jqGrid**  
This workflow requires jqGrid.  
Download jqGrid from [HERE](http://www.trirand.com/blog/?page_id=6).  
After downloading, extract the following two files: *"ui.jqgrid.css"* and *"jquery.jqGrid.min.js"*.  
Copy the two files to `/portal/static/js/vendor/jqgrid/` inside the Bluecat Gateway container.  
Create a *"jqgrid"* directory if it does not exist.   


## Usage   

1. **Set Office 365 Configurations**  
![screenshot](img/absorbaroo1.jpg?raw=true "absorbaroo1")  

Select the *Office 365* tab and set the following parameters:  
- Instance Name:  
Select the route parameter from the drop down menu.  
This optional parameter specifies the instance to return the version for. If omitted, all instances are returned.  
Valid instances are: Worldwide, China, Germany, USGovDoD, USGovGCCHigh.  

- Client Request ID  
A GUID is required for client association. Generate a GUID for each machine that calls the web service. Refer [HERE](https://docs.microsoft.com/en-us/Office365/Enterprise/office-365-ip-web-service) for more information.  

- Service Areas  
Check or uncheck the service areas you wish to whitelist.  
If you are unsure, check all.  

Click *"SAVE"*  

2. **Set DNS Edge Configurations**  
![screenshot](img/absorbaroo2.jpg?raw=true "absorbaroo2")   

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

- Domain List  
Type in the domain list which corresponds to the Office 365 whitelist.  
Make sure the specified domain list is preregistered in the DNS Edge CI.     

Click *"SAVE"*   

3. **Set Meraki Cloud Controller Parameters**  
![screenshot](img/absorbaroo3.jpg?raw=true "absorbaroo3")   

Select the *SDWAN* tab and set the following parameters:  
- API Key:  
This will be the API key for a specific user to login to the Meraki cloud controller via API.  
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
The updated firewall rules will be set above this keyword (phrase), meaning any rule below this keyword will not be overwritten.  
Typically a *"Deny All Traffic"* rule will be set here so that only the updated firewall rules based on DNS Edge domain lists will be allowed through.  

![screenshot](img/sdwan_fw9.jpg?raw=true "sdwan_fw9")  

Click *"SAVE"*   

4. **Set Polling Intervals**  
![screenshot](img/absorbaroo4.jpg?raw=true "absorbaroo4") 

Select the *Execution* tab and set polling intervals.  
- Current Endpoint Version:  
The current endpoint version will be shown here.   

- Last Synchronized at:  
The last synchronized time will be shown here.  

- Interval (sec):  
Specify polling intervals.  

Click *"SYNCHRONIZE NOW"* to synchronize and start intervals.  
If you wish to manually synchronize once without intervals, type in *"0"* in the interval menu and click *"SYNCHRONIZE NOW"*.  
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
ABSORBAROO is the brainchild of the BlueCat JAPAC team. Thank you for contributing your time to making this project a success.  

The Team:  
- David Jones (djones@bluecatnetworks.com)  
- Michael Nonweiler (mnonweiler@bluecatnetworks.com)  
- Akira Goto (agoto@bluecatnetworks.com)  
- Timothy Noel (tnoel@bluecatnetworks.com)  
- Ryu Tamura (rtamura@bluecatnetworks.com)  

Date: 2019-04-25  
Gateway Version: 18.10.2

## License
©2019 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved. This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted. Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.
