# Device Registration Portal

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>
    <h2 style="display: inline-block">Table of Contents</h2>
  </summary>
  <ol>
    <li>
      <a href="#about">About</a>
    </li>
    <li>
      <a href="#bam-setup">BAM Setup</a>
      <ul>
        <li><a href="#setup-udf">Setup UDFs</a></li>
        <li><a href="#setup-tag-group">Setup Tag Group</a></li>
        <li><a href="#add-location">Setup Location</a></li>
        <li><a href="#add-zone">Add Zone</a></li>
        <li><a href="#add-ip-network">Add IP Network</a></li>
        <li><a href="#deploy-server">Deploy Server</a></li>
      </ul>
    </li>
    <li><a href="#deployment">Deployment</a>
      <ul>
          <li><a href="#deploy-docker-container">Deploy Docker Container</a></li>
        <li><a href="#assign-specific-write-privileges">Assign specific write privileges</a></li>
      </ul>
    </li>
    <li><a href="#workflows-ui">Workflows UI</a>
      <ul>
        <li><a href="#register-device-ui">Register Device UI</a></li>
        <li><a href="#update-device-ui">Update Device UI</a></li>
        <li><a href="#search-ui">Search UI</a></li>
      </ul>
    </li>
    <li><a href="#reference">Reference</a>
      <ul>
        <li><a href="#rest-api-document">Rest API Document</a></li>
        <li><a href="#property-options">Property Options</a></li>
      </ul>
    </li>
  </ol>
</details>

## About
The BlueCat Device Registration Portal provides a single, centralized API and UI for making instant registers and management for network devices where the management of that data is spread across multiple accounts, groups, location, networks and DNS providers.


## Requirements

- BlueCat Gateway Version: 22.4.1 or greater
- BAM/BDDS Version: 9.4 or greater
- Windows Server Version: 2012 or later


## BAM setup

### Setup focus database
   1. Add license to workflow
   2. Add host entry to BAM:
    
        ```
        ssh root@<BAM IP>
        su admin
        configure database
        add access <IP address>
        save
        exit
        
        where:
            <BAM IP>             IP of BlueCat Address Manager
            <IP address>         Access IP Address
        ```
   
   3. Add access method:
    
        ```
        Access to directory : /etc/postgresql/9.6/main
        sudo nano pg_hba.conf
        add the following line in #IPv4 local connections section: "host all postgres <IP Address>/32 md5"
        
        where:
            <IP address>         Access IP Address
        ```
      
   4. Reboot BAM
        ```
        su admin
        reboot
        ```

### Setup UDFs


   1. In BAM **Administration** under **Data Management**, select **Migration**
   2. Click **Browse** and upload attach migration XML file *portal-udfs.xml*
   3. Click **Queue** button to add UPFs

   ![Setup UDF](images/migration.png?raw=true)



### Setup Tag Group

Support for <a href="#register-device-ui">Register Device UI</a> 

#### Device Registration Tag Group

   1. Create new Tag name **Device Registration** in **Groups**

   ![Device Tag](images/tag.png?raw=true)
   
   3. Create **Device Group** Tags in **Service Registration**
   
   > Example: Computer, Workstation, Server ...

   ![Device Tag](images/create_tag.png?raw=true)
   
   3. In each **Device Group** Tag add preference to select default Device Group in Register Device Page
   
   > Preference are used to display default Device Group in Register Device page

   ![Device Tag](images/Preference.png?raw=true)


### Setup Location

Support for <a href="#register-registration-ui">Register Device UI</a> 

#### Device Registration Location

   1. Select **Locations** in **Group**
   
   2. Select **Country** and **City** in **Location**
   
   > Example: New Zealand (NZ), Dunedin (NZ DUD)

   ![Location](images/city.png?raw=true)
   
   3. In each **City** create **Location**
   
   > Example: Lab 1 (NZ DUD L1)

   ![Location](images/location.png?raw=true)


### Add Zone
#### If don't want to setup manual, please use the add zone API in **Rest API Document**. Go to <a href="#rest-api-document">Rest API Document</a>

1. Select the **Configuration** > **View** > **Zone**
2. Add.
3. Add **Location code**
4. Under **Deployment Roles**, click **New** and select **DNS Role**.
5. Under Role, select a DNS deployment role from the Type drop-down menu: `Master` or `Hidden Master` (BAMv9.3 is `Primary`)
6. Click **Select Server Interface**.
- Under **Servers**, click a server name
- Under **Server Interfaces**, select the server interface and click **Add**.
7. Click **Add**.
8. In Zone, under Details, add Tag in **Device Registration** tag group to add current zone to **Device Group**

![Zone](images/new_zone.png?raw=true)


#### Note: zone must be added  **Deployable**
   

### Add IP Network

Support for <a href="#register-device-UI">Register Device UI</a>.


1. Select the **Network Block** to add new **Network**
2. Under **Blocks** and **Networks**, click the **New** button, select **IPv4Network**
3. Set required fields
4. Select **Location**
5. Click **Add**.
6. In NetWork, under Details, add Tag in **Device Registration** tag group to add current Network to **Device Group**
 
![Network](images/network.png?raw=true)

### Deploy Server

Only for BlueCat DNS Server.

1. Select the **Server** tab
2. Under **Servers**, select the check box for one or more BDDS Servers.
3. Click **Action** and **select Deploy**.
4. Under **Confirm Server Deploy**, review the list of servers to be updated, then under **Services**, select
the **DNS**
5. Click **Yes**

![Deploy BDDS](images/deploy.png?raw=true)


## Deployment
### Deploy Docker Container

1. Pull image from Registry:

    ```
    docker login registry.bluecatlabs.net/
    docker pull <image-registry-name>:<tag>
    ```
    
    > Example: docker pull registry.bluecatlabs.net/professional-services/japac-tma/device_registration:drp-22.1-rc1

    Or copy the <drp-image>.tar.gz file to the host machine and run cmd:
    
    ```
    docker load -i <drp-image>.tar.gz
    ```

2. Run Gateway Container
    
    If Hybrid DNS Update only:

    ```
    docker run -d --name <container-name> -p <port>:8000  \
                  -e BAM_IP=<bam-ip>                      \
                  <image-name>:<tag>
    
    Where
            <port>                     Port of Gateway
            <bam-ip>                   IP of BAM
            <image-name>:<tag>         Can use Image name or ID
   
    ```
    Note: 
    - Optional environment variables to configure logger properties as: 
        ```
        -e ADMIN_USERNAME=<admin-username>
        -e ADMIN_PASSWORD=<admin-password>
        
        Where
                                            
             <admin-username>         Name of the BlueCat Gateway user that will be used to provide linked Loccation, IP Network and DNS Domain from tag Device Group for non-admin user.
             <admin-password>         Encrypted password for the BlueCat Gateway user that will be used to provide linked Loccation, IP Network and DNS Domain from tag Device Group for non-admin user.                    
        
        ```

    - If Device Registration Portal with Gateway version *22.4.1* or later:
      1. Additional to `environment`:
      - `SESSION_COOKIE_SECURE`=`false`
      2. Configure **Security** in Gateway UI:
      - **Content Security Policy** to accept to load CSS by enter URLs to `Policy` input
      - **Cache Control**: `No Cache`

      ![Cache Control](images/cache_control.png?raw=true)
    

## Workflow UI

### Register Device
   
   1. Input the corresponding information:
    
       | Fields                          | Description                                                     |
       |-----------------------------------------------------------------| --- |
       | `Description`                   | Description of new Device                                       |
       | `MAC Address`                   | MAC address of Device                                           |
       | `Name`                          | Name of Device. Must be name without space                      |
       | `Device Group`                  | Group of new Device.                                            |
       | `Location`                      | Location of new Device                                          |
       | `IP Network (Subnet)` | IP Network of new Device IP address                             |
       | `IP Network Detail`             | Displayed details of the selected IP Network                    |
       | `DNS Domain`                      | DNS Domain of new Device host record.                           |
       | `Account ID` | Account ID of new Device                                        |
       | `IP Address`             | IP address from the selected IP Network, assigned to new Device |
       
      ![Register Device](images/register_device.png?raw=true)

>   Note: Add button is enable while user imported name, account ID and valid MAC address.
    Clear button is used to clear name, account ID, MAC address fields and display default Device Group, Location, IP Network and DNS Domain.
      
   2. Examples for MAC address formats:

       | MAC Address                 |
       | --- |
       | 1A2B3C4d5e6f      |
       | 1A:2B:3C:4d:5e:6f |
       | 1a:2:3:4:5:6      |
       | 1A-2B-3C-4d-5e-6f |
       | 1A2B.3C4d.123     |

   3. Register New Device:
   - To register a new device, first the user has to enter the device’s MAC address in the **MAC Address** field.
   - The **Device Group**, **Location**, **IP Network**, and **DNS Domain** can be selected from the dropdown list.
   - The **Add** button is disabled when **Mac Address**, **Name** and **Account ID** are empty.
   - Click **Add** button to add new device.
   - Click **Clear** button to clear input data.
    
### Update Device

   1. Input the corresponding information:
    
       | Fields                | Description                                                        |
       |--------------------------------------------------------------------| --- |
       | `Description`         | Description of Device. Updatable                                   |
       | `MAC Address`         | MAC address of Device. Non-updatable                               |
       | `Name`                | Name of Device. Must be name without space. Updatable              |
       | `Device Group`        | Group of Device. Non-updatable                                     |
       | `Location`            | Location of Device. Non-updatable                                  |
       | `IP Network (Subnet)` | IP Network of Device IP address. Non-updatable                     |
       | `IP Network Detail`   | Displayed details of the selected IP Network                       |
       | `DNS Domain`          | DNS Domain of Device host record. Non-updatable                    |
       | `Account ID`          | Account ID of Device. Updatable                                    |
       | `IP Address`          | IP address from the selected IP Network, assigned to Device        |
       | `Audit`               | Audit data of Device. Display create and lastest 4 update sessions |
       | `User`                | Name of user, created or updated Device                            |
       | `Action`              | Action create or update Device                                     |
       | `Date/Time`           | Time of audit sessions in format                                   |
       
      ![Update Device](images/update_device.png?raw=true)

>   Note: User can update Description, Name and Account ID.


### Search

   1. Input the corresponding information:
    
       | Fields                | Description                                           |
       |-------------------------------------------------------| --- |
       | `MAC Address`         | MAC address of Device.                                |
       | `Name`                | Name of Device. Must be name without space.           |
       | `Device Group`        | Group of Device.                                      |
       | `Location`            | Location of Device.                                   |
       | `IP Network (Subnet)` | IP Network of Device IP address.                      |
       | `IP Network Detail`   | Displayed details of the selected.                    |
       | `DNS Domain`          | DNS Domain of Device host record.            |
       | `Account ID`          | Account ID of Device.                        |
       | `IP Address`          | IP address from the selected IP Network, assigned to Device |
       
      ![Search](images/search.png?raw=true)


>   Note: User can search devices by 4 options:
> - Mac Address 
> - Name 
> - IP Address 
> - Device Group, Location, IP Network and DNS Domain


## Reference
### Rest API Document
 
Access UI API Document in **http://`ip`:`port`/api/v1/**
> Example: http://192.168.88.170:5000/api/v1/
