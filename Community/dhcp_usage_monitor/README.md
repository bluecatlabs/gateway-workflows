# DHCP Usage Monitor

**Bluecat Gateway Version:** 22.4.1 and greater  
**BAM Version:** 9.4.0 and greater

This workflow will retrieve specified block / network information from BAM and monitor / show the overall DHCP usage within that specified block / network. A typical use case of this workflow would be when you need to monitor the overall usage of DHCP either within a large block where many networks exists or within a network with multiple DHCP ranges.

## Prerequisites

1. **BAM Default Configuration**  
   This workflow will be using the default configuration value in `/portal/bluecat_portal/config.py` in BlueCat Gateway container. To set the default configuration, in BlueCat Gateway, go to Administration > Configurations > General Configuration.  
   In General Configuration, select the BAM Settings tab and enter the configuration name under "Default Configuration:" and save.  
   ![screenshot](img/BAM_default_settings.jpg?raw=true 'BAM_default_settings')

2. **BAM Access Configuration**  
   This workflow will access the BAM database via SQL.  
   In order to gain access to BAM you must first configure the BAM database settings to allow access the BlueCat Gateway IP address.  
   Refer to the BAM Administration Guide for more details.

3. **Additional Python3 packages**  
   This workflow requires the following additional python3 packages.

   > _psycopg2_, _pytz_, _apscheduler_, _pysnmp_

   Install additional packages using PIP3 inside the BlueCat Gateway container.

   ```
   $pip3 install psycopg2 pytz apscheduler pysnmp
   ```

4. **jqGrid**  
   This workflow requires jqGrid.  
   Download jqGrid from [HERE](http://www.trirand.com/blog/?page_id=6).  
   After downloading, extract the following three files: _"ui.jqgrid.css"_, _"jquery.jqGrid.min.js"_ and _"grid.locale-xx.js"_.  
   _"grid.locale-xx.js"_ will change depending on the locale you choose to use.  
   (For instance, for Japan it will be _"grid.locale-ja.js"_)  
   Copy _"ui.jqgrid.css"_ and _"jquery.jqGrid.min.js"_ under `/portal/static/js/vendor/jqgrid/` inside the Bluecat Gateway container.  
   Create a new directory `jqgrid` under `/portal/static/js/vendor/` if none exists.  
   Copy _"grid.locale-xx.js"_ under `/portal/static/js/vendor/jqgrid/i18n/` inside the Bluecat Gateway container.  
   Create a new directory `i18n` under `/portal/static/js/vendor/jqgrid` if none exists.

5. **BAM user**  
   This workflow requires a BAM user with the following credentials.

   > BlueCat Gateway UDF: all  
   > User Type: Administrator  
   > User Access Type: GUI and API

   Create a user in BAM if not created.  
   Refer to the BAM Administration Guide for more details.

## Setting Up

1. **Populate config file**  
   Open _config.json_ file and populate the following section.
   > _BAM_IP_: IP address of BAM  
   > _BAM_user_: Unique user name in BAM  
   > _BAM_pass_: Password for the user  
   > _execution interval_: The interval of checking the DHCP usage (in seconds). The default value is 60  
   > _trap_servers_: Do not populate and ignore at this time

## Usage

1. **Create CSV file**  
   Create a CSV file which has "Block", "Pool Name", "Network", "Gateway", "Tag Name", "DHCP Range" data.  
   For example:

```csv
Block, Pool Name, Network, Gateway, Tag Name, DHCP Range
10.112.0.0/16, MacPool1, 10.112.194.0/24, , NetworkTag1, 10.112.194.30-10.112.194.254
10.112.0.0/16, MacPool2, 10.112.200.0/24, , NetworkTag2, 10.112.200.30-10.112.200.254
10.114.0.0/16, MacPool3, 10.114.203.0/24, 10.114.203.254, , 10.114.203.30-10.112.203.253
10.114.0.0/16, MacPool3, 10.114.205.0/24, 10.114.205.254, NetworkTag4, 10.114.205.30-10.112.205.253
```

**Block**: Specify a block in CIDR format. If the specified block doesn't exist in BAM, it will create one for you.

**Pool Name**: (optional) Specify the name of the MAC Address Pool to which you wish to link the Allow MAC Pool DHCP deployment option to. The specified MAC Pool needs to exist in BAM in advance. The Allow MAC Pool DHCP deployment option will be set at the specified **_block_** level. When not specified, no Allow MAC Pool DHCP deployment option will be set.

**Network**: Specify a network in CIDR format. If the specified network doesn't exist in BAM, it will create one for you.

**Gateway**: (optional) Specify the default gateway IP address for the network. When not specified, the default gateway IP address will be the default one when networks are created.

**Tag Name**: (optional) Specify a Tag name if you wish to tag the network to a shared network tag. If the specified tag name doesn't exist in BAM, it will create one for you. A Tag Group must exist in BAM in advance.

**DHCP Range**: Specify the DHCP range within the network. The format is {Starting IP}-{Ending IP}.

2. **Import CSV file**  
   Click "Choose File" and select the corresponding CSV file.  
   The _IP Address List_ will be populated as below:  
   ![screenshot](img/Bulk_DHCP1.jpg 'Bulk_DHCP1')

3. **Create DHCP Range (with block/network etc) in BAM**  
   Click "REGISTER".  
   ![screenshot](img/Bulk_DHCP2.jpg 'Bulk_DHCP2')

4. **Check BAM to see results**

---

## Additional

1. **Language**  
   You can switch to a Japanese menu by doing the following.

   1. Create _ja.txt_ in the BlueCat Gateway container.  
      `cd /portal/Administration/create_workflow/text/ cp en.txt ja.txt`
   2. In the BlueCat Gateway web UI, go to Administration > Configurations > General Configuration.  
      In General Configuration, select the _Customization_ tab.  
      Under _Language:_ type in `ja` and save.  
      ![screenshot](img/langauge_ja.jpg?raw=true 'langauge_ja')

2. **Appearance**  
   This will make the base html menus a little bit wider.
   1. Copy all files under the directory `additional/templates` to `/portal/templates` inside the Bluecat Gateway container.

## Author

- Akira Goto (agoto@bluecatnetworks.com)
- Ryu Tamura (rtamura@bluecatnetworks.com)

## License

©2022 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved. This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted. Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.
