IoT Device Registration

IoT device registration workflow integrated into BlueCat Gateway and Aruba
Clearpass API allowing self-service registrations to authorised users and RunDeck
scheduled de-registration of expired devices, written in Python. Compliant to
organisation Network Access Control using Aruba Clearpass.


Features:
 - User authentication managed through BlueCat Address Manager
 - Upload CSV file containing multiple IoT Devices for registration
 - Validates MAC Addresses before processing for registration
 - MAC Addresses are automatically added into Aruba Clear
 - Email notification of successful and failed registration of IoT devices
 - IoT devices assigned with DHCP Reserved IP address and DNS resolvable host
 - Automated de-registration of IoT devices that has reached expired period

 
Detailed Information:
- The workflow contains a configuration file "iotipallocation.conf" that has to be configured prior to using it, the configuration includes BAM's connectivity, API User credentials, the block and network to use for the DHCP Reserved allocation, the zone for creation of the device name in DNS, email server settings for notifications and other information necessary for the workflow to workflow
- The workflow has a UI to get the username, email address and the list of IoT Devices to be registered in CSV format
- Format of the CSV file: name,macAddress,department,phone,location,period


System Requirements:
 - BlueCat Address Manager
 - BlueCat Gateway
 - Aruba Clearpass
 - Python v3 or higher


Installation:
 - Download workflow and import into Gateway
 - Assign access rights to the workflow
 
 
 Configuration:
  - Aruba Clearpass, create an API Client account with generated shared key, appropriate
    access rights to allow the API Client to perform add and delete of MAC Addresses
  - Allow BlueCat Gateway to communicate with BlueCat Address Manager by configuring appropriate network firewall rules
  - Sample "iotipallocation.conf"

[BAMCONFIG]
configuration = ACME
networks = 172.17.48.0/20,172.17.64.0/20
locations = block1,block2
taggroup = IOT
iotview = Internal
iotdomain = iot.acme.corp
ddservers = HQ NS1,HQ NS2

[IOTSETTINGS]
expire = 60

[MAILSETTINGS]
mailhost = 10.0.1.249
mailuser = ismanager1
mailpass = Bluecatno.1
maildomain = acme.corp
ssl = false

[CLEARPASS]
client_id=bc_iot
client_secret=Otq8H0YjBE3+sf4lML9MU/SJDztouoUe9L4U3iz1r7q4
grant_type=client_credentials
apihost=10.0.1.248
description=This device was automatically registered via BlueCat IOT Device Registration
attributes={"Device Type": "ACME_IOT"}

[DEBUG]
enable = true


Future Roadmap:
- A simple interface to upload and preview CSV File, username and contact information retrieved from BAM
- Setting of configuration in workflow UI instead of accessing directly via CLI


