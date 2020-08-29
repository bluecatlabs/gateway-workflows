# **Certified Selective Deployment Workflow**
## Select a DNS record for deployment

**BlueCat Gateway Version:** 18.6.1 and greater <br/>
**BAM version:** 8.3.2 and greater <br/>
**DNS/DHCP Server version:** 8.3.2 and greater <br/>

### Dependencies
DNS/DHCP server appliances should be configured with necessary deployment roles and be under Address Manager control. Full deployment to DNS/DHCP server required prior to performing selective deployment. <br/>

### Description/Example Usage
In addition to Python wrappers for the Selective Deployment APIs, Certified Selective Deployment workflows are now available on the BlueCat Labs GitHub repository, helping to complete BlueCat’s Integrity solution of this API feature with UI-based Gateway workflows.

There is a standalone Selective Deployment workflow as well as new Add, Update, and Delete Host Record workflows that include the ‘Deploy Now’ functionality. BlueCat recommends using these workflows as a template that you can modify to suit the needs of your environment.

By default, all Certified Selective Deployment workflows invoke the selectiveDeploy API method using the ‘related’ property. This will deploy a record and any of its associated records. These Certified workflows use related deployments as a precaution against broken record chains if modifying or deleting records.  

For more details on the Selective Deployment API methods, refer to the DNS Integrity Gateway Help & Documentation or Administration Guide, or the Address Manager 8.3.2 API Guide available on BlueCat Customer Care.

___
**Note**

Before you begin, you must import the Selective Deployment Workflow either by downloading it manually from GitHub, or through the GitHub Import function in the BlueCat Gateway UI. Once it is imported, you must set the necessary permissions for the workflow.
___

### Using the Selective Deployment Workflow
Select or search for a DNS record that has previously been added or modified. Once you search for a DNS record, a table displays all DNS records. You can select and deploy DNS records in the table. The status of deployment is displayed in the same form.

To use the Selective Deployment workflow:
1. Login to BlueCat Gateway.
2. Click **Certified > Deployment**.
3. Select **Selective Deployment Example**.
4. In the drop-down menus, select the Configuration, View, and Zone.
5. Click **Search DNS**. The table populates with related DNS records.
6. Select the check boxes at the end of each row for each DNS record you want to deploy, then click **Deploy**. The system returns either a Success, Queued, or an explanation of failure message.

### Add, Delete, and Update Host Record Certified Workflows
These workflows are the same workflows as previously found on Github, however, these workflows include a **Deploy Now** checkbox, which invokes the selective deployment API. These workflows are purely example templates for you to modify for your use.

To use the Host Record workflow:
1. Select the Configuration, View, Zone, Host Record, Name, and IPv4 Address.
2. Select the **Deploy Now** check box, and click **Submit**. The system returns either a Success, Queued, or an explanation of failure

___
**Note**

When you are working with selective deployment, keep in mind the following:

* If you navigate away from the form, you will lose the  
  deployment status.
* If you add a new record and deploy while waiting for a 
  previous deployment, the status message of the previous deployment will be overwritten.
___

©2020 BlueCat Networks (USA) Inc. and its affiliates (collectively ‘ BlueCat’). All rights reserved.
This document contains BlueCat confidential and proprietary information and is intended only for the person(s) to whom it is transmitted.
Any reproduction of this document, in whole or in part, without the prior written consent of BlueCat is prohibited.
