# ROLE MANAGEMENT UI

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
        <li><a href="#adding-DNS-deployment-role">Adding  DNS deployment roles</a></li>
        <li><a href="#adding-DNS-deployment-option">Adding DNS deployment options</a></li>
      </ul>
    <li><a href="#deployment">Deployment</a>
      <ul>
          <li><a href="#deploy-docker-container">Deploy Docker Container</a></li>
        <li><a href="#assign-specific-write-privileges">Assign specific write privileges</a></li>
      </ul>
    </li>
    <li><a href="#workflows-ui">Workflows UI</a>
      <ul>
        <li><a href="#get-dns-deployment-roles-ui">Get DNS Deployment Roles UI</a></li>
        <li><a href="#dns-deployment-roles-detail-ui">DNS Deployment Roles Details UI</a></li>
        <li><a href="#validate-actions-ui">Validate Actions UI</a></li>
        <li><a href="#action result-ui">Action Result UI</a></li>
      </ul>
    </li>
    <li><a href="#dns-deployment-role-actions">DNS Deployment Role Actions</a>
      <ul>
        <li><a href="#copy-role-to-server">Copy DNS Deployment Role To Server</a></li>
        <li><a href="#move-role-to-server">Move DNS Deployment Role To Server</a></li>
        <li><a href="#copy-role-to-zones">Move DNS Deployment Role To Zones</a></li>
        <li><a href="#add-servers">Add Servers</a></li>
        <li><a href="#publish-roles">Publish DNS Deployment Roles</a></li>
        <li><a href="#hide-roles">Hide DNS Deployment Roles</a></li>
      </ul>
    </li>
    <li><a href="#workflows-ui">Known Issues</a></li>
    <li><a href="#reference">Reference</a>
      <ul>
        <li><a href="#rest-api-document">Rest API Document</a></li>
      </ul>
    </li>
  </ol>
</details>

## About
Deployment roles determine the services provided by a server. A deployment role creates a client-facing service, specified with an IP address, on a network or published server interface. Each server interface can have multiple DNS roles. The BlueCat Role Management provides a centralized UI workflow for making instant actions to manage DNS deployment roles where the management of that data is spread across multiple DNS servers, DNS forwarding and reverse zones.

## Requirements

- BlueCat Gateway Version: 22.11.1 or greater
- BAM/BDDS Version: 9.5 or greater

## BAM setup
### Adding DNS Deployment Role

1. DNS Deployment Role

Deployment roles determine the services provided by a server. A deployment role creates a client-facing service, specified with an IP address, on a network or published server interface. Each server interface can have multiple DNS roles and one DHCP role. When multiple roles are assigned, the most locally-specified server role takes precedence. For example, if deployment roles are set at both the DNS view and DNS zone level, the role set at the zone level applies to the DNS zone. Roles set to None aren't deployed.

When assigning deployment roles, you select a server and server interface for the role. Only servers that support the deployment role are available to be selected, so you can't assign a deployment role to a server that doesn't support the role. For example, you can't add DHCP deployment roles to a DNS Caching server.
You can set DNS deployment roles for the following:

- IPv4 and IPv6 blocks (reverse zone)
- IPv4 and IPv6 networks (reverse zone)
- DNS views
- DNS zones

2. Adding DNS deployment roles

You can add multiple DNS deployment roles to a single server.

The most local role takes precedence for any section of the configuration. At a minimum, DNS roles must be applied at the view level for DNS deployment to occur. For reverse DNS, a DNS deployment role must be applied to either a block or network to create the reverse DNS settings for that object and its children.

To add or edit a DNS deployment role:

 Where it's available, click the Deployment Roles tab.
 Under Deployment Roles, click New and select DNS Role.
 Under Role, select a DNS deployment role from the Type drop-down menu:
- Primary—deploys files and settings to create a DNS primary server.
- Hidden Primary—deploys files and settings to create a DNS primary, but without name server and glue records, thus hiding the server from DNS queries.
- Secondary—deploys files and settings to create a DNS secondary server.
- Stealth Secondary—deploys files and settings to create a DNS secondary but, without name server and glue records, thus hiding the server from DNS queries.
- Forwarder—deploys a forwarding zone in BIND, or conditional forwarding in Microsoft DNS, to forward queries for a specific zone to one or more DNS servers. Forwarding requires that recursion be enabled; recursion is automatically enabled when you select the Forwarder role.
- Stub—deploys a zone that contains only the name server records for a domain. Stub zones don't contain user-selected settings or options.
- Recursion—used when creating a caching-only DNS server that accepts recursive queries, but doesn't host any zones. This role must be set at the view level; required deployment options are set automatically when you deploy the configuration.
- None—clears all data from the server to which it's applied.

 Under Server Interface, set the servers for the deployment role:

 - Click Select Server Interface.
 - Click a server name to display a list of server interfaces. Click Up to return to the list of servers.
 - Select the button for the server interface that you want to add.
 - Click Add. The selected server interface opens in the Servers section.
 - Click Remove to remove a server from the list.

 When you select the Primary or Hidden Primary option in the Role section, a Name server record section will be available. Under Name server record, select the time-to-live value for name server and glue records that are deployed via deployment roles.

 - Recommended (1 day)—this option is selected by default when adding a DNS Primary or Hidden Primary deployment role.
 - Use Zone Default Setting—if selected, the zone TTL value will be used. Upgraded roles will use this option by default.
 - Specify—select this option to manually set the time-to-live value for the record. Enter a value in the field, then select either Seconds, Minutes, Hours, or Days from the drop-down menu. If you have upgraded roles from a previous version, you can use this option to change the value.

When you select the Secondary, Stealth Secondary, Forwarder, or Stub option in the Role section, a Zone Transfers section opens after you select a server interface.

 - Click Select Server Interface.
 - Click a server name to display a list of server interfaces. Click Up to return to the list of servers.
 - Under Server Interfaces, select the button for the server interface that you want to add: Service interface, Management Interface, or Published Interface (if available).
 - Click Add. The selected server interface opens in the Zone Transfers section.
 - Click Remove to remove a server from the list.

Under Change Control, add comments, if required.

Click Add or Add Next to add another deployment role. 

### Adding DNS Deployment Options

1. DNS Deployment Option

DNS deployment options

DNS deployment options define the deployment of Address Manager DNS services. Address Manager supports most of the options used by both BIND and Microsoft DNS.

For deployment options that take an IP address, ACL name, or TSIG key as a parameter, select the type of parameter you want to add from the drop-down list presented when defining the option.

- To specify an IP address or name, select IP Address or name. Type the address or name in the text field and click Add.
- To specify a TSIG key, select Key. A drop-down list appears and lists the TSIG keys available in the Address Manager configuration. Select a key from the list and click Add.
- To specify an ACL, select ACL. A drop-down list showing pre-defined and custom DNS ACLs available in the current Address Manager configuration appears. Select an ACL from the drop-down menu and click Add.

You can set DNS Deployment options for the following Address Manager objects:

- Configurations
- Server Groups
- Servers
- DNS Views
- DNS Zones
- IPv4 Blocks
- IPv4 Networks
- IPv6 Blocks
- IPv6 Networks

2. Adding DNS Deployment Options

DNS deployment options can be set at various points of the configuration including the configuration, view, and zone levels. Options set at the configuration level are inherited by all views and zones within that configuration.

Options set at the view level are inherited by all zones under that specific view. By default, options set at the zone level apply to that zone and are inherited by all child zones of that zone, unless the options are overridden. When DNS option inheritance is disabled, options attached to a zone apply only to the specific zone itself. Both DNS and DHCP options can be set at the configuration level whereas only DNS options and SOA records can be configured at the view level and below.

To add DNS deployment options:

- From the configuration drop-down menu, select a configuration.
- Select the DNS tab. Tabs remember the page you last worked on, so select the tab again to ensure you're on the Configuration information page.
- Navigate to the level at which you want to set a DNS deployment option and click the Deployment Options tab. Deployment Options tabs appear at the configuration, view, zone, IP block, and IP network levels.
- Under Deployment Options, click New and select DNS Option.
- Under General, select the option and set its parameters.
     - Option—select a DNS client deployment option from the drop-down menu. When an option is selected, parameter fields for the option appear.
- Under Servers, select the servers to which the option will apply:
     - All Servers—applies the deployment option to all servers in the configuration.
     - Server Group—applies the deployment option to a specific server group in the configuration. Select a server group from the drop-down menu.
     - Specific Server—applies the deployment option to a specific server in the configuration. Select a server from the drop-down menu.
- Under Change Control, add comments, if required.
- Click Add.

## Deployment
### Deploy Docker Container

1. Pull image from Registry:

    ```
    docker login registry.bluecatlabs.net/
    docker pull <image-registry-name>:<tag>
    ```

    Or copy the .tar.gz file to the host machine and run cmd:
    
    ```
    docker load -i <image>.tar.gz
    ```

2. Run Gateway Container

    ```
    docker run -d --name <container-name> -p <port>:8000  \
                  -e BAM_IP=<bam-ip>                      \
                  <image-name>:<tag>
    
    Where
            <port>                     Port of Gateway
            <bam-ip>                   IP of BAM
            <image-name>:<tag>         Can use Image name or ID


    ```

## Workflow UI
### Get DNS Deployment Role

   ![Get_Role](images/get_role.png?raw=true)

### DNS Deployment Role Details

   ![Role_Details](images/role_details.png?raw=true)

### Validate Actions

   ![Validation](images/validation.png?raw=true)

### Action Result

   ![Action Result](images/result.png?raw=true)


## DNS Deployment Role Actions
### Copy DNS Deployment Role To Server
### Move DNS Deployment Role To Server
### Copy DNS Deployment Role To Zones
### Add Servers
### Publish DNS Deployment Roles
### Hide DNS Deployment Roles


## Reference
### Rest API Document
 
Access UI API Document in **http://`ip`:`port`/role-management/v1/**
> Example: http://192.168.88.170:5000/role-management/v1/