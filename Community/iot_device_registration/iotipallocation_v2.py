#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
# By: Muhammad Heidir (mheidir@bluecatnetworks.com)
# Date: 03-04-2019
# Gateway Version: 18.10.2
# Description: Bulk IoT Device Registration/De-Registration workflow for BlueCat Gateway

import sys, os, re, json, csv, time, traceback, ipaddress
from flask import g
from bluecat.api_exception import PortalException
from configparser import ConfigParser
from datetime import datetime
from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .iotcommon import readConfigFile, sendMail, isInteger, deployServerServices, cpGetClient, cpAddMac

# ClearPass API library Setting
DEBUG = False

# Configuration File
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__)) + os.path.sep
CONFIG_FILE = CURRENT_DIR + 'iotipallocation.conf'
LOG_FILE = 'iotipallocation.log'

# Regular Expression for Validation MAC Address
MACREGEX = re.compile('(^([a-fA-F0-9]{2}[-]{1}){5}[a-fA-F0-9]{2}$)|(^([a-fA-F0-9]{2}[:]{1}){5}[a-fA-F0-9]{2}$)|(^[a-fA-F0-9]{12}$)')


def parseCSVFile(netLoc, expireTime, csvFile, owner, email):
    """ Parses the CSV file and process the contents for errors, returns iotInformation as dictionary """
    iotInformation = {}
    iotIndex = 0
    validIndex = 0
  
    currentDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    expireDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  
    with open(csvFile, mode='r') as iotFile:
        csvReader = csv.DictReader(iotFile, fieldnames=['name', 'macAddress', 'department', 'phone', 'location', 'period'])
        
        LOGGER.debug("(parseCSVFile) " + str(netLoc))
        # Process and insert into dictionary with iotIndex as Index
        for row in csvReader:
            if iotIndex != 0 or "name" not in row['name']:
                if isMacValid(row['macAddress']):
                    if int(row['period']) > int(expireTime):
                        expireDate = (datetime.now() + timedelta(days=expireTime)).strftime('%Y-%m-%d 23:59:59')
                    else:
                        expireDate = (datetime.now() + timedelta(days=int(row['period']))).strftime('%Y-%m-%d 23:59:59')
                    
                    # Check if the location in the CSV matches with the pre-defined locations
                    if netLoc.get(row['location']) != None:
                        iotInformation[iotIndex] = {'name': row['name'], 
                                                    'macAddress': convertMac(row['macAddress']),
                                                    'registration': currentDate, 
                                                    'expire': expireDate, 
                                                    'macState': True,
                                                    'email': email,
                                                    'department': row['department'],
                                                    'phone': row['phone'],
                                                    'location': row['location'],
                                                    'owner': owner
                                                    }
                        # Successfully processed
                        validIndex += 1

                    else:
                        # Since the location does not match any in the list, add into error list
                        iotInformation[iotIndex] = {'name': row['name'], 
                                                    'macAddress': row['macAddress'], 
                                                    'registration': currentDate, 
                                                    'macState': False,
                                                    'email': email,
                                                    'department': row['department'],
                                                    'phone': row['phone'],
                                                    'location': row['location'],
                                                    'owner': owner
                                                    }
                        LOGGER.warning("(parseCSVFile) Invalid_Location Line:" + str(iotIndex + 1) + " Name:" + row['name'] + " MAC:" + row['macAddress'] + " Location:" + row['location'])
                else:
                    # If there is an error with the entry, add into error list
                    iotInformation[iotIndex] = {'name': row['name'], 
                                                'macAddress': row['macAddress'], 
                                                'registration': currentDate, 
                                                'macState': False,
                                                'email': email,
                                                'department': row['department'],
                                                'phone': row['phone'],
                                                'location': row['location'],
                                                'owner': owner
                                                }
                    LOGGER.warning("(parseCSVFile) Invalid_MAC Line:" + str(iotIndex + 1) + " Name:" + row['name'] + " MAC:" + row['macAddress'])

            # Increment Line Counter
            iotIndex += 1
  
    LOGGER.debug("(parseCSVFile) Contents: " + str(iotInformation))
    LOGGER.info("(parseCSVFile) " + ">>>>>> Number of valid MAC: " + str(validIndex) + "/" + str(iotIndex))
    return iotInformation


def validateArguments(args):
    """ Validates the number of arguments and return dictionary containing user, email and csv file directory """
    # Example: ['iotipallocation_v2.py', 'user', 'hello@acme.corp', 'iotmachine.csv']
    user = args[1]
    email = args[2]
    csvFile = args[3]
  
    if isValidEmail(email) and os.path.isfile(csvFile):
        return {'user': user, 'email': email, 'csvFile': csvFile}
    raise Exception("(validateArguments) Invalid arguments provided. Check arguments.")
  

def isMacValid(macAddress):
    """ Returns True for a valid Mac Address, False otherwise """
    if MACREGEX.match(macAddress):
        return True
    return False

  
def isValidEmail(email):
    """ Returns True for a valid email address, False otherwise """
    if len(email) > 7:
        if re.match("^.+@([?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?))$", email) != None:
            return True
    return False


def convertMac(macAddress):
    """ Performs conversion of Mac Address format to the colon type and return as string """
  # Reference: https://forums.freebsd.org/threads/python-inserting-a-sign-after-every-n-th-character.26881/
 
  # Convert to CAPS
    stdMac = str(macAddress).upper()
  
  # Checks if contains '-' character and replace with ':'
    if "-" in stdMac:
        return stdMac.replace('-', ':')
    elif ":" in stdMac:
        return stdMac
    else:
        return ':'.join([ i+j for i,j in zip(stdMac[::2],stdMac[1::2])])

    
def removeMacColons(macAddress):
    """ Removes colon character from Mac Address """
    return macAddress.replace(':', '')


def sendNotifyMail(mailSettings, recipientName, recipient, iotInfo):
    """ Send notification email to requestor containing successful and failed registration of IoT devices """
    sender = mailSettings['mailuser'] + "@" + mailSettings['maildomain']
    helpdeskemail = "it.helpdesk@acme.corp"
    
    # Email to Admin
    adminMsg = MIMEMultipart('alternative')
    adminMsg['Subject'] = "IOT Device Registration"
    adminMsg['From'] = "BlueCat Gateway <" + sender +">"
    adminMsg['To'] = "BlueCat Admin <" + sender +">"

    # Email to Owner
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "IOT Device Registration"
    msg['From'] = "BlueCat Admin <" + sender +">"
    msg['To'] = recipientName + "<" + recipient + ">"
    
    noErrorMsg = "<html><h1>IOT Device Registration</h1>\n\n" + \
                    "<p>This is a system generated email. Do not reply to this email.</p>\n" + \
                    "<p><strong>Owner:</strong> " + recipientName + " </p>\n" + \
                    "<p><strong>Email:</strong> " + recipient + "</p>\n" + \
                    '<table border="1" cellpadding="1" cellspacing="1" style="width: 800px;">' + "\n" + \
                    "<caption>IOT Device Information</caption>\n" + \
                    "<thead>\n" + \
                    "<tr>\n" + \
                    ' <th scope="col">Name</th>\n' + \
                    ' <th scope="col">MAC Address</th>\n' + \
                    ' <th scope="col">IP Address</th>\n' + \
                    ' <th scope="col">Host Name</th>\n' + \
                    ' <th scope="col">Registration</th>\n' + \
                    ' <th scope="col">Expiration</th>\n' + \
                    "</tr>\n" + \
                    "</thead>\n" + \
                    "<tbody>\n "
  
    withErrorMsg =  '<br><br><table border="1" cellpadding="1" cellspacing="1" style="width: 500px;">' + "\n" + \
                      "<caption>IOT Device With Errors</caption>\n" + \
                      "<thead>\n" + \
                      "<tr>\n" + \
                      ' <th scope="col">Name</th>\n' + \
                      ' <th scope="col">MAC Address</th>\n' + \
                      ' <th scope="col">Registration</th>\n' + \
                      ' <th scope="col">Reason</th>\n' + \
                      "</tr>\n" + \
                      "</thead>\n" + \
                      "<tbody>\n "
  
    for iot in iotInfo:
        regDate = datetime.strptime(iotInfo[iot]['registration'], "%Y-%m-%d %H:%M:%S")

        if iotInfo[iot]['macState'] and iotInfo[iot].get('address') != None:
            expDate = datetime.strptime(iotInfo[iot]['expire'], "%Y-%m-%d %H:%M:%S")
            noErrorMsg += "<tr>\n" + \
                            "<td>%s</td><td>%s</td><td>%s</td><td>%s</td>\n" % (iotInfo[iot]['name'], iotInfo[iot]['macAddress'], iotInfo[iot]['address'], iotInfo[iot]['host']) + \
                            '<td><span style="color: rgb(0, 0, 0); font-family: Arial, Verdana, Helvetica, sans-serif; font-size: 11px;">%s</span></td>' % regDate.strftime("%b %d, %Y %H:%M:%S") + "\n" + \
                            '<td><span style="color: rgb(0, 0, 0); font-family: Arial, Verdana, Helvetica, sans-serif; font-size: 11px;">%s</span></td>' % expDate.strftime("%b %d, %Y %H:%M:%S") + "\n" + \
                            "</tr>\n"
        else:
            # Checks whether the problem is caused by unable to assign an IP Address
            if iotInfo[iot].get('addressId') != None and iotInfo[iot]['addressId'] == 0:
                withErrorMsg += "<tr>\n" + \
                              "<td>%s</td><td>%s</td>\n" % (iotInfo[iot]['name'], iotInfo[iot]['macAddress']) + \
                              '<td><span style="color: rgb(0, 0, 0); font-family: Arial, Verdana, Helvetica, sans-serif; font-size: 11px;">%s</span></td>' % regDate.strftime("%b %d, %Y %H:%M:%S") + "\n" + \
                              "<td>%s does not have available IP address for assignment</td>\n" % iotInformation[iot]['location'] + \
                              "</tr>\n"
            
            # Checks whether the problem is caused by invalid location
            elif netLoc.get(iotInfo[iot]['location']) == None:
                withErrorMsg += "<tr>\n" + \
                              "<td>%s</td><td>%s</td>\n" % (iotInfo[iot]['name'], iotInfo[iot]['macAddress']) + \
                              '<td><span style="color: rgb(0, 0, 0); font-family: Arial, Verdana, Helvetica, sans-serif; font-size: 11px;">%s</span></td>' % regDate.strftime("%b %d, %Y %H:%M:%S") + "\n" + \
                              "<td>%s does not exist</td>\n" % iotInformation[iot]['location'] + \
                              "</tr>\n"
            # If none of the above, then it is caused by an invalid MAC Address
            else:
                withErrorMsg += "<tr>\n" + \
                              "<td>%s</td><td>%s</td>\n" % (iotInfo[iot]['name'], iotInfo[iot]['macAddress']) + \
                              '<td><span style="color: rgb(0, 0, 0); font-family: Arial, Verdana, Helvetica, sans-serif; font-size: 11px;">%s</span></td>' % regDate.strftime("%b %d, %Y %H:%M:%S") + "\n" + \
                              "<td>Invalid MAC Address or IP Address is currently active.</td>\n" + \
                              "</tr>\n"
    
    noErrorMsg += "</tbody>\n" + \
                    "</table>\n\n\n" + \
                    withErrorMsg + \
                    "</tbody>\n" + \
                    "</table>\n" + \
                    "\n<p>You can now connect your IoT device to the network and access it using the IP Address/Hostname above" + \
                    "\nShould you encounter any issue, please contact IT HelpDesk (%s)</p></html>\n\n" % helpdeskemail

    # Attach email for Owner
    msg.attach(MIMEText(noErrorMsg, 'html'))

    # Attach email for Administrator
    adminMsg.attach(MIMEText(noErrorMsg, 'html'))

    # Send email to Owner
    sendMail(mailSettings['mailhost'], sender, recipient, msg.as_string())
    # Send email to Administrator
    sendMail(mailSettings['mailhost'], sender, sender, adminMsg.as_string())



def checkIotState(tag_group, iotDevice):
    """ Check expire state of IoT based on its Mac Address and information located in tag object """
    LOGGER.info("(checkIotState) Checking IoT State against existing Tag Objects")
    try:
        iotTag = tag_group.get_tag_by_name(iotDevice['macAddress'])
        iotTagProperties = iotTag.get_properties()

        if "false" in iotTagProperties['expireState'].lower():
            LOGGER.info("(checkIotState) MAC Address exists and still valid.")
            return {'action': "none", 'state': True, 'iotTag': iotTag}
        else:
            LOGGER.info("(checkIotState) MAC Address exists and expired. New IP Address will be assigned")
            return {'action': "update", 'state': False, 'iotTag': iotTag}

    except:
        LOGGER.info("(checkIotState) Unable to locate MAC Address in Tag.")
        return {'action': "create", 'state': False}


def createTag(tag_group, iotInfo, addressEntity):
    """ Performs tag creation with information in BlueCat Address Manager, returns the tag ID upon successful creation """
    LOGGER.info("(createTag) Creating tag containing IoT Information")
    properties = addressEntity.get_properties()
    tagProperties = (
        "email=" + iotInfo['email']
        + "|expire=" + iotInfo['expire']
        + "|expireState=false" 
        + "|ipaddress=" + properties['address'] 
        + "|registration=" + iotInfo['registration'] 
        + "|department=" + iotInfo['department'] 
        + "|phone=" + iotInfo['phone'] 
        + "|location=" + iotInfo['location'] 
        + "|owner=" + iotInfo['owner'] 
        + "|iotname=" + iotInfo['name']
        ) 
    # Creates tag and returns its entity id
    return tag_group.add_tag(properties['macAddress'], tagProperties)


def updateTag(bam, tag, email, expire, ipaddress, registration):
    """ Performs tag update when new registration is performed with updated expiration date """
    LOGGER.info("(updateTag) Updating tag information with IoT Device Information: " + str(oldTagEntity))
    try:
        tag.set_properties({
            "email": email,
            "expire": expire,
            "expireState": "false",
            "ipaddress": ipaddress,
            "registration": registration
            })
        tag.update()
        LOGGER.info("(updateTag) Successfully updated tag: " + str(tag))
        return True
    except Exception as err:
        LOGGER.error("(updateTag) Unable to update tag:" + str(tag) + " Error:" + str(err))
    return False


def populateNetworksId(bam, bam_configuration, bamConfig):
    """ Populate the network IDs based on the list of networks defined in iotipallocation.conf to facilitate getNextAvailableIP API call to BAM """
    # Get list of Id for the networks
    networksId = {}

    for location, network in bamConfig['netloc'].items():
        networkAddress = str(ipaddress.IPv4Network(network).network_address)
        networkEntity = bam_configuration.get_ip_range_by_ip("IP4Network", networkAddress)
        if networkEntity.get_property("CIDR") == network:        
            networksId[location] = networkEntity.get_id()
        else:
            LOGGER.warning("(populateNetworksId) Looking for " + network + " but found " + networkEntity.get_property("cidr"))

    bamConfig['networksId'] = networksId
    LOGGER.debug("(populateNetworksId) Networks Id:" + str(bamConfig['networksId']))


def getAddressRangeForLocation(bam, networksId, location):
    """ Returns entity object reference by network ID """
    LOGGER.debug("(getAddressRangeForLocation)")
    return bam.get_entity_by_id(int(networksId[location]))


def assignIP(bam, bam_configuration, networksId, iotdomain, iotview, iotInfo):
    """ Assigns DHCP Reserved IP Address for newly registered IoT Device """
    LOGGER.debug("(assignIP) iotviewId: " + str(iotview.get_id()))

    hostInfo = iotInfo['name'] + "." + iotdomain + "," + str(iotview.get_id()) + ",true,false"
    properties = "name=" + iotInfo['name'] + "|excludeDHCPRange=true"

    # Process IP Assignment
    addressRange = getAddressRangeForLocation(bam, networksId, iotInfo['location'])
    LOGGER.debug("addressRange: " + str(addressRange))

    try:
        #addressEntity = addressRange.assign_next_available_ip4_address(iotInfo['macAddress'], hostInfo, "MAKE_DHCP_RESERVED", properties)
        addressEntity = addressRange.assign_next_available_ip4_address(iotInfo['macAddress'], hostInfo, "MAKE_DHCP_RESERVED", properties)
        #addressEntity = addressRange.get_next_available_ip4_address()
        LOGGER.debug("(assignIP) addressEntity: " + str(addressEntity))

        
        return addressEntity
    except PortalException:
        LOGGER.error("(assignIP) Unable to assign IP Address to MAC Address, check networks have enough free IP Addresses before proceeding")
  
    # # Assign IP to MAC Address, loop until assigned successfully
    # while networkIdsItr < networkIdsLength:
    # # Start from the first network Id
    #     networkId = bamConfig['networksId'][networkIdsItr]

    # # Assign IP
    #     addressEntity = bam.assignNextAvailableIP4Address(int(bamConfig['configurationId']), int(networkId), iotInfo['macAddress'], hostInfo, "MAKE_DHCP_RESERVED", properties)
    
    # # In case the network Id is full, try the next one
    #     networkIdsItr += 1
    
    #return addressEntity
    return False   


def iot_ip_allocation(csvFile, iotUser, iotEMail):
    """ Process CSV file and perform registration of IoT devices which includes registering of MAC address into Aruba Clearpass for Network Access Control to allow network connectivity """
    global LOGGER
    LOGGER = g.user.logger

    LOGGER.info("IOT IP Allocation started: " + str(datetime.now()))
    
    bam = g.user.get_api()
    
    try:
        BAMCONFIG, IOTSETTINGS, MAILSETTINGS, CLEARPASS = readConfigFile(CONFIG_FILE)
    except Exception as err:
        raise Exception("(main) Configuration file error: " + str(err))
       
    # Parse CSV, validate and extract its contains
    iotInformation = parseCSVFile(
        BAMCONFIG['netloc'], IOTSETTINGS['expire'],
        csvFile, iotUser, iotEMail)

    
    # Get Configuration Id
    LOGGER.info("(main) Getting configuration Id: " + str(BAMCONFIG['configuration']))
    bam_configuration = bam.get_configuration(BAMCONFIG['configuration'])

    # Get Tag Group Id
    LOGGER.info("(main) Getting Tag Group: " + str(BAMCONFIG['taggroup']))
    tag_group = bam.get_tag_group_by_name(BAMCONFIG['taggroup'])
    
    LOGGER.info("(main) Getting View: " + str(BAMCONFIG['iotview']))
    iotview = bam_configuration.get_view(BAMCONFIG['iotview'])

    # Initialization of function-wide variables for error-checking, device information and count
    addressEntity = {}
    iotNoErrorIdx = 0
    iotErrorInfo = {}
    iotErrorIdx = 0
    errorProc = False

    # Check if networksId map has already been populated, before calling assignIP
    # (could it be provided in the config file?)
    if BAMCONFIG.get("networksId") == None:
        populateNetworksId(bam, bam_configuration, BAMCONFIG)
    networksId = BAMCONFIG['networksId']

    # Start processing each key in iotInformation dictionary 
    for key in iotInformation:
        
        # Process only if key contains an Integer, which contains a valid Iot Device
        # There are other key such as "lastMailCount" and "iotIndex" which is used to
        # ensure the correct IoT Device information is being processed
        if iotInformation[key]['macState']:
            # Display current processing IoT Device index
            LOGGER.info("(main) Index: " + str(key) + "    iot: " + str(iotInformation[key]))
          
            # Store iotInformation[key] contents for Administrator to receive information should any error encountered during processing
            iotInfo = str(iotInformation[key])
        
            try:
                # Checks whether Tag Object already exists, check state
                iotState = checkIotState(tag_group, iotInformation[key])
                
                ##
                # If expired and exists, assign new IP address and update IoT Device Information
                if not iotState['state'] and "update" in iotState['action']:
                    LOGGER.info("(main) Updating MAC Address with new IP Address and IoT Device Information")

                    # Get and assign and IP address to the IoT Device
                    addressEntity[key] = assignIP(
                        bam, bam_configuration, networksId, BAMCONFIG['iotdomain'], iotview, iotInformation[key])
                    iotInformation[key]['addressId'] = addressEntity[key].get_id()
                    LOGGER.debug("(main) addressEntity[key]: " + str(addressEntity[key]))

                    if not addressEntity[key].is_null():
                        properties = addressEntity[key].get_properties()
                        
                        # Update tag with updated IP Address information
                        updateTag(iotState['iotTag'], iotInformation[key]['email'], iotInformation[key]['expire'], properties['address'], iotInformation[key]['registration'])
                        LOGGER.info("(main) Update tag processed")
                  
                        # If successfully linked IP address with Tag Object, extract IP Address properties and send email to requestor
                        try:
                            iotState['iotTag'].link_entity(addressEntity[key])
                            LOGGER.info("(main) Successfully link tag to IP Address")
                        
                            # Append IP Address information into existing dictionary
                            iotInformation[key]['address'] = properties['address']
                            iotInformation[key]['host'] = iotInformation[key]['name'] + "." + BAMCONFIG['iotdomain']
                        
                            # Increment IoT Device process count
                            iotNoErrorIdx += 1
                            errorProc = False

                        except:
                            # Raise error value to True, since Tag Object cannot be linked with IP Address
                            LOGGER.warning("(main) Unable to link tag to IP Address. Check MAC Address and IP Allocation.")
                            errorProc = True      
                    else:
                        # Raise error value to True, unable to assign IP Address
                        LOGGER.warning("(main) Unable to assign IP Address. Check network size on: " + iotInformation[key]['location'])
                        # Set state to False to highlight problem with device while assigning IP Address
                        iotInformation[key]['macState'] = False
                        errorProc = True
                ##
                # If does not exists, create new IP address assignment and create IoT Device Information
                elif not iotState['state'] and "create" in iotState['action']:
                    LOGGER.info("(main) Creating new IP Address assignment and IoT Device Information")

                    # Get and assign an IP address to the IoT Device
                    addressEntity[key] = assignIP(
                        bam, bam_configuration, networksId, BAMCONFIG['iotdomain'], iotview, iotInformation[key])
                    iotInformation[key]['addressId'] = addressEntity[key].get_id()
                    LOGGER.debug("(main) addressEntity[key]: " + str(addressEntity[key]))

                    if not addressEntity[key].is_null():
                        # Create a tag linking the MAC Address with IoT Device Information 
                        tagId = createTag(tag_group, iotInformation[key], addressEntity[key])
                        iotInformation[key]['tagId'] = tagId
                        LOGGER.debug("(main) tagId: " + str(iotInformation[key]['tagId']))
                        tag = bam.get_entity_by_id(tagId)

                        # If successfully linked IP address with Tag Object, extract IP Address properties and send email to requestor
                        try:
                            tag.link_entity(addressEntity[key])
                            LOGGER.info("(main) Successfully link tag to IP Address")

                            properties = addressEntity[key].get_properties()
                            
                            # Append IP Address information into existing dictionary
                            iotInformation[key]['address'] = properties['address']
                            iotInformation[key]['host'] = iotInformation[key]['name'] + "." + BAMCONFIG['iotdomain']
                            
                            # Increment IoT Device process count
                            iotNoErrorIdx += 1
                            errorProc = False

                        except:
                            # Raise error value to True, since Tag Object cannot be linked with IP Address
                            LOGGER.warning("(main) Unable to link tag to IP Address. Check MAC Address and IP Allocation.")
                            errorProc = True
                    # Unable to assign IP to device
                    else: 
                        # Raise error value to True, unable to assign IP Address
                        LOGGER.warning("(main) Unable to assign IP Address. Check network size on: " + iotInformation[key]['location'])
                        # Set state to False to highlight problem with device while assigning IP Address
                        iotInformation[key]['macState'] = False
                        errorProc = True
                  # Since MAC Address exists and still valid, just processs the next IoT Device
                else:
                    # Append offending IoT Device information for sending to Administrator
                    iotErrorInfo[iotErrorIdx] = iotInformation[key]
                    iotErrorIdx += 1
                    pass                

            except Exception as err:
                # Raise error when unable to assign IP address to Device
                LOGGER.error(err)
                LOGGER.debug(traceback.print_exc(limit=5)) 
                errorProc = True
                
                # Continue to process next IoT Device
                pass
        
        # Since MAC Address is invalid, take note of the entry for reporting
        else:
            # Append offending IoT Device information for reporting purposes
            iotErrorInfo[iotErrorIdx] = iotInformation[key]
            iotErrorIdx += 1
            
    #########################################################    
    # End of iterating all IoT Device information, show count
    LOGGER.info("(main) Number of IoT Devices processed: " + str(iotNoErrorIdx))

    # Checks for number of IoT Devices processed, if not zero, proceed to deploy services with updated configuration
    if iotNoErrorIdx > 0:
        LOGGER.debug("(main) " + str(iotInformation))
        LOGGER.info("(main) Proceeding to deploy DDS with updated information")
        deployServerServices(bam_configuration, BAMCONFIG['ddServers'])

    
    #####################################################################
    # Aruba Clearpass portion, to add MAC Address for MAC Authentication
    #####################################################################

    LOGGER.info("(main) Starting Aruba Clearpass MAC Address registration")
    if CLEARPASS['apihost']:
        apiclient = cpGetClient(CLEARPASS['apihost'], DEBUG, CLEARPASS['client_id'], CLEARPASS['client_secret'])
    else:
        apiclient = None
        
    # Start processing each key in iotInformation dictionary 
    for key in iotInformation:
    
        # Process only if key contains an Integer, which contains a valid Iot Device
        # There are other key such as "lastMailCount" and "iotIndex" which is used to
        # ensure the correct IoT Device information is being processed
        if iotInformation[key]['macState']:
            endpoint = {'mac_address': removeMacColons(iotInformation[key]['macAddress']),
                        'status': "Known",
                        'description': CLEARPASS['description'],
                        'attributes': CLEARPASS['attributes']
                        }
            if apiclient:
                cpAddMac(apiclient, endpoint)
            LOGGER.debug("(main->cpAddMac) MAC Address added into Aruba Clearpass: " + str(endpoint))
    
    #####################################################################
          
    # If error encountered, notify Administrator via email and to check email for more information
    if iotNoErrorIdx != len(iotInformation):
        LOGGER.debug(iotErrorInfo)
        LOGGER.warning("(main) " + str(len(iotErrorInfo)) + " invalid entries found while processing MAC Addresses")
        LOGGER.info("(main) Valid MAC Addresses successfully processed and registered into BlueCat Address Manager")
  
    else:
        LOGGER.info("(main) Valid MAC Addresses successfully processed and registered into BlueCat Address Manager")
        
    if MAILSETTINGS["mailhost"]:
        sendNotifyMail(MAILSETTINGS, iotUser, iotEMail, iotInformation)

# RELEASE NOTES
# 20190220 - v2.1
# - Made changes to network block to accept network block IDs instead of network block names
# - To facilitate the POC
