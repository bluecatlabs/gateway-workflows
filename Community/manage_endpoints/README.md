# Portal for Endpoint Registration and IP Address Management

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
        <li><a href="#rest-api-documentation">REST API Documentation</a></li>
        <li><a href="#property-options">Property Options</a></li>
      </ul>
    </li>
  </ol>
</details>

## About
This portal for endpoint registration and IP address management provides a self-service UI for managing the registration of devices on the network. Each device is registered with a unique MAC address and is assigned to a device group. Most registered devices also have a fixed IP address assigned that is registered in DNS and reserved in DHCP.



## Requirements

- BlueCat Gateway Version: 22.4.1 or greater
- BAM/BDDS Version: 9.4 or greater


## BAM setup

### Setup database access for Gateway
   1. Add Gateway host IP addresses to database ACL on BAM:
    
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
   
   Alternative method:

   1. Add Gateway host IP addresses to database ACL on BAM:
    
        ```
        Access to directory : /etc/postgresql/9.6/main
        sudo nano pg_hba.conf
        add the following line in #IPv4 local connections section: "host all postgres <IP Address>/32 md5"
        
        where:
            <IP address>         Access IP Address
        ```
      
   2. Reboot BAM
        ```
        su admin
        reboot
        ```

### Add User-Defined fields to Address Manager object schema


   1. In BAM **Administration** under **Data Management**, select **Migration**
   2. Click **Browse** and upload attach migration XML file *portal-udfs.xml*
   3. Click **Queue** button to add UDFs

   ![Setup UDF](images/migration.png?raw=true)



### Setup Tag Group

Create a Tag Group to manage device groups. Devices (MAC address objects) must be linked to a device group before they can be managed in the <a href="#register-device-ui">Register Device UI</a> 

#### Device Registration Tag Group

   1. Create new Tag name **Device Registration** in **Groups**

   ![Device Tag](images/tag.png?raw=true)
   
   3. Create **Device Group** Tags in **Device Registration**
   
   > Example: Computer, Workstation, Server ...

   ![Device Tag](images/create_tag.png?raw=true)
   
   4. In each **Device Group** Tag set the preference field to select the default Device Group in the Register Device page
   
   > Preference fields are used to select the default Device Group in the Register Device page

   ![Device Tag](images/Preference.png?raw=true)


### Setup Location

The <a href="#register-registration-ui">Register Device UI</a> uses a new location field on MAC address objects, 
where the location is a location code from the Locations group in Address Manager

#### Add locations for Device Registration

   1. Select **Locations** in **Group**
   
   2. Select **Country** and **City** in **Location**
   
   > Example: New Zealand (NZ), Dunedin (NZ DUD)

   ![Location](images/city.png?raw=true)
   
   3. In each **City** create **Location**
   
   > Example: Lab 1 (NZ DUD L1)

   ![Location](images/location.png?raw=true)


### Add Zone
#### If don't want to add zones manually, use the add zone API in **REST API Documentation**. Go to <a href="#rest-api-document">REST API Documentation</a>

1. Select the **Configuration** > **View** > **Zone**
2. Add.
3. Add **Location code**
4. Under **Deployment Roles**, click **New** and select **DNS Role**.
5. Under Role, select a DNS deployment role from the Type drop-down menu: `Primary` or `Hidden Primary`
6. Click **Select Server Interface**.
- Under **Servers**, click a server name
- Under **Server Interfaces**, select the server interface and click **Add**.
7. Click **Add**.
8. In Zone, under Details, add Tag in **Device Registration** tag group to add current zone to **Device Group**

![Zone](images/new_zone.png?raw=true)


#### Note: the **Deployable** flag on the zone must be enabled
   

### Add IP Network

Support for <a href="#register-device-UI">Register Device UI</a>.


1. Select the **Network Block** to add new **Network**
2. Under **Blocks** and **Networks**, click the **New** button, select **IPv4Network**
3. Set required fields
4. Select **Location**
5. Click **Add**.
6. In Network, under Details, add a Tag from the **Device Registration** tag group to add current Network to **Device Group**
 
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

1. Pull image from a docker registry:

    ```
    docker login <docker-registry-name>
    docker pull <image-registry-name>:<tag>
    ```
    
    > Example: docker pull quay.io/university_nam_portal:22.1

    Or copy the <image>.tar.gz file to the host machine and run cmd:
    
    ```
    docker load -i <image>.tar.gz
    ```

2. Run Gateway Container
    
    To deploy the Gateway container on Docker:

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
                                            
             <admin-username>         Name of the BlueCat Gateway machine user that will be used to access Address Manager to search for linked Location, IP Network and DNS Domain from tag Device Group for non-admin user.
             <admin-password>         Encrypted password for this user               
        
        ```

    - To encrypt the password, either use the /encrypt/credential/ API in a running instance, or use:
       ```
       read PASSWORD
       docker run --rm -i <image-name>:<tag> python3 - $PASSWORD <<EOF
       <<EOF
       from sys import argv
       from bluecat.util.util import encrypt_key
       print(encrypt_key(argv[1].encode()).decode())
       EOF
       ```

    - Configure Gateway security and cache control:
      1. To enable unencrypted HTTP connections to Gateway within a secure network, add to the docker environment:
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

>   Note: Add button is enabled when the user has entered a name, an account ID and a valid MAC address.
    Clear button is used to clear name, account ID, MAC address fields and display the default Device Group, Location, IP Network and DNS Domain.
      
   2. Examples of supported MAC address formats:

       | MAC Address                 |
       | --- |
       | 1A2B3C4d5e6f      |
       | 1A:2B:3C:4d:5e:6f |
       | 1a:2:3:4:5:6      |
       | 1A-2B-3C-4d-5e-6f |
       | 1A2B.3C4d.123     |

   3. Register a new device:
   - To register a new device, first the user has to enter the device’s MAC address in the **MAC Address** field.
   - The **Device Group**, **Location**, **IP Network**, and **DNS Domain** can be selected from the dropdown list.
   - The **Add** button is disabled when **MAC Address**, **Name** and **Account ID** are empty.
   - Click **Add** button to add new device.
   - Click **Clear** button to clear input data.
    
### Update Device

   1. These fields are displayed:
    
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

>   Note: The user can update Description, Name and Account ID.


### Search

   1. Input information in the fields you want to search on, and leave other fields empty:
    
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


>   Note: The following searches are available. Search by:
> - MAC Address 
> - Name 
> - IP Address 
> - Device Group, Location, IP Network and DNS Domain


## Reference
### Rest API Documentation
 
Access Swagger-UI API documentation at **http://`<host>`:`<port>`/api/v1/**
> Example: http://192.0.2.170/api/v1/
