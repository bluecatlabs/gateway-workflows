# **Certified Cisco ACI Workflow**
This workflow applies to BlueCat customers who have transitioned to the Cisco ACI infrastructure for their data centers.

### Requirements
**BlueCat Gateway version:** 20.3.1 and greater <br/>
**BAM version:** 9.1.0 and greater <br/>

### Description/Example Usage
This Certified Cisco ACI workflow allows you to populate Address Manager with data from your Cisco ACI environment. Using this workflow, you can import ACI Tenants and their infrastructure as well as ACI Fabric Devices into Address Manager for visibility alongside your DNS, DHCP, and IPAM infrastructure in BAM.

You can import the following:
  * ACI Fabric Devices
    *  APICs
    *  SPINEs
    *  LEAFs
  * Tenants
    * Private Networks
    * Bridge Domains
    * Subnets
    * Endpoint Devices
  * Additional meta-data such as End Point Groups

BAM organizes the Tenant Infrastructure using Tab Groups, Tags, and Configurations. You can use Configuration Groups in BAM 9.1.0 or greater to help you organize Tenants.

ACI Fabric Devices appear as Device Subtypes under the Cisco ACI Infrastructure Device Type (Groups > Device Types > Device Subtypes).

The diagram below illustrates the mapping between the Cisco ACI infrastructure and BAM:


<img src="ACI-BAM_mapping.png"/>

___
**Note**

The Cisco ACI workflow only imports data from the Cisco APIC to Address Manager. It does not import data from Address Manager.
___
___
**Note**

Before you begin, you must import the Cisco ACI workflow either by downloading it manually from GitHub, or through the GitHub Import function in the BlueCat Gateway UI. Once it is imported, you must set the necessary permissions for the workflow.
___

### Using the Cisco ACI workflow
You can search for Cisco ACI tenants in the infrastructure by providing your Cisco APIC IP address, username, and password. As an option, you can import ACI Fabric Devices such as APIC, SPINE, and LEAF switches to the selected BAM configuration. Once you search for tenants, a table displays all tenants in the Cisco APIC. You can then select which tenants to import into Address Manager.

To use the Cisco ACI workflow:
1. Log in to BlueCat Gateway.
2. Click **Certified > Cisco ACI**.
3. In the fields, enter your APIC IP address, username, and password.
4. [Optional] Import the ACI Fabric. Perform this step if you want to import APIC, SPINE, and LEAF devices to the selected BAM configuration.

  1. Select **Import ACI Fabric Devices to**.
  2. In the drop-down, select the configuration.
  3. Click **Import Fabric**.   


5. Click **Discover Tenants**. The table populates with the tenants in the infrastructure.
6. Choose which tenants to import (by default, all tenants and options are selected upon discovery). Click **Deselect All**/**Select All** to deselect or select all tenants in the table. For each tenant in the table, you can select or deselect the following:

     * **Import** - select to import the tenant
     * **Import Endpoint Devices** - select to import endpoint devices
     * **Overwrite Existing** - select to overwrite the existing tenant in BAM

     ___
     **Note**

     You can adjust the number of tenants displayed in the table by selecting a number in the **Show entries** drop-down. You can also refine the table by entering a word in the **Filter** field.
     ___

7. Click **Import Infrastructure**.

Once you click **Import Infrastructure**, a pop-up opens that displays the progress of the import operation.
___
**Attention**

Importing tenants may take a prolonged period of time depending on the number of tenants and the complexity of your infrastructure.
___

### FAQ

**Do I need Cisco ACI credentials to use this workflow?**

Yes. You must have ACI credentials to use this workflow. Contact your Cisco administrator to obtain credentials. You cannot search for tenants without these credentials.

**Can I use an earlier version of Address Manager?**

You can only use Address Manager v9.1.0 or greater. Earlier versions are not compatible with the Cisco ACI workflow.

**Can I deploy changes I've made to my tenants in BAM to my ACI environment?**

No. Currently, the Cisco ACI workflow only imports ACI Tenants and Fabric Devices into Address Manager, and cannot push changes back to the ACI environment.

**How do I troubleshoot error messages?**

Each section of the Cisco ACI workflow will display error messages relevant to that section. For example, if you have the wrong ACI credentials, you will see the appropriate error message in the UI. If you still cannot resolve the issue based on the UI error message, please refer to the log files for more detailed information.

**Why can't I import ACI Fabric Devices? I'm getting an error message in the UI.**

When importing ACI Fabric Devices, you might see the following error message:

```
An error occurred! Please check the user logs for the
current session for more information. The log can be found
in the BlueCat logs folder  at: <logfile.log>
```

This message can mean the ACI Fabric Devices have already been imported, or that any associated objects have already been imported. For example, when importing an APIC, SPINE, or LEAF, a network block or network for an associated device might also have been previously imported resulting in the error message. Please refer to the log files for more specific information to help you resolve the conflict.

©2020 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved.
This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted.
Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.
