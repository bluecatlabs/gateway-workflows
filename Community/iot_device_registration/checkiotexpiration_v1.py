#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
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

from flask import g
import bluecat.api_exception
import sys, json, os, time, traceback
from configparser import ConfigParser
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .iotcommon import readConfigFile, sendMail, deployServerServices, cpGetClient, cpDelMac


# ClearPass API library Setting
DEBUG = False

####################### DEFAULT SETTINGS ######################
## DO NOT EDIT! THESE ARE DEFAULT VALUES. TO CHANGE, CREATE
# Configuration File
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__)) + os.path.sep
CONFIG_FILE = CURRENT_DIR + 'iotipallocation.conf'
LOG_FILE = 'iotipallocation.log'
######################### DO NOT EDIT ###############################


def removeMacChars(macAddress):
    """ Return MAC Address with symbols (:,-) removed and characters compacted. eg: 11:22:33:AA:BB:CC -> 112233AABBCC """
    if '-' in macAddress:
        return macAddress.replace('-', '')
    elif ':' in macAddress:
        return macAddress.replace(':', '')
    else:
      return macAddress


def sendAdminNotifyMail(mailSettings, iotInfo):
    """ Send a notification email to Administrator containing list of expired IoT devices that has been de-registered """
    LOGGER.info("(sendAdminNotifyMail) Preparing email for Administrator")
    sender = mailSettings['mailuser'] + "@" + mailSettings['maildomain']
    helpdeskemail = "it.helpdesk@acme.corp"
    
    # Email to Admin
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Expired IOT Device Removal"
    msg['From'] = "BlueCat Gateway <" + sender +">"
    msg['To'] = "BlueCat Admin <" + sender +">"
    
    msgHtml = "<html><h1>Expired IOT Device Removal</h1>\n\n" + \
                    "<p>This is a system generated email. Do not reply to this email.</p>\n" + \
                    '<table border="1" cellpadding="1" cellspacing="1" style="width: 800px;">' + "\n" + \
                    "<caption>IOT Device Information</caption>\n" + \
                    "<thead>\n" + \
                    "<tr>\n" + \
                    ' <th scope="col">Owner</th>\n' + \
                    ' <th scope="col">Department</th>\n' + \
                    ' <th scope="col">Email</th>\n' + \
                    ' <th scope="col">Contact</th>\n' + \
                    ' <th scope="col">Location</th>\n' + \
                    ' <th scope="col">Name</th>\n' + \
                    ' <th scope="col">MAC Address</th>\n' + \
                    ' <th scope="col">IP Address</th>\n' + \
                    ' <th scope="col">Registration</th>\n' + \
                    ' <th scope="col">Expired Date</th>\n' + \
                    "</tr>\n" + \
                    "</thead>\n" + \
                    "<tbody>\n "
  
    for iot in iotInfo:
        iotProperties = iot.get_properties()
        regDate = datetime.strptime(iotProperties['registration'], "%Y-%m-%d %H:%M:%S")
        expDate = datetime.strptime(iotProperties['expire'][:-2], "%Y-%m-%d %H:%M:%S")
        
        msgHtml += "<tr>\n" + \
                        "<td>%s</td>\n" % iotProperties['owner'] + \
                        "<td>%s</td>\n" % iotProperties['department'] + \
                        "<td>%s</td>\n" % iotProperties['email'] + \
                        "<td>%s</td>\n" % iotProperties['phone'] + \
                        "<td>%s</td>\n" % iotProperties['location'] + \
                        "<td>%s</td>\n" % iotProperties['iotname'] + \
                        "<td>%s</td>\n" % iot['name'].replace('-', ':') + \
                        "<td>%s</td>\n" % iotProperties['ipaddress'] + \
                        '<td><span style="color: rgb(0, 0, 0); font-family: Arial, Verdana, Helvetica, sans-serif; font-size: 11px;">%s</span></td>' % regDate.strftime("%b %d, %Y %H:%M:%S") + "\n" + \
                        '<td><span style="color: rgb(0, 0, 0); font-family: Arial, Verdana, Helvetica, sans-serif; font-size: 11px;">%s</span></td>' % expDate.strftime("%b %d, %Y %H:%M:%S") + "\n" + \
                        "</tr>\n"
        
    
    msgHtml += "</tbody>\n" + \
                    "</table>\n\n\n" + \
                    "\n<p>Should you encounter any issue, please contact IT HelpDesk (%s)</p></html>\n\n" % helpdeskemail

    # Attach email for Administrator
    msg.attach(MIMEText(msgHtml, 'html'))

    # Send email to Administrator
    sendMail(mailSettings['mailhost'], sender, sender, msg.as_string())
    LOGGER.info("(sendAdminNotifyMail) Administrator email sent")


def sendUserNotifyMail(mailSettings, iotInfo):
    """ Send notification email to device owner with list of expired IoT devices that has been removed """
    LOGGER.info("(sendUserNotifyMail) Preparing email for users")

    sender = mailSettings['mailuser'] + "@" + mailSettings['maildomain']
    helpdeskemail = "it.helpdesk@acme.corp"
    userEmail = []
    
    # Identify matching email addresses and tabulate into array
    for iot in iotInfo:
        iotProperties = iot.get_properties()
        if len(userEmail) == 0:
            email = iotProperties['email']   
            userEmail.append(email)
            
        elif iot['properties']['email'] not in userEmail:
            email = iotProperties['email']
            userEmail.append(email)
    
    # Tabulate all email addresses, uniquely
    for email in userEmail:
        # Email to User
        msg = []
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Expired IOT Device Removal"
        msg['From'] = "BlueCat Gateway <" + sender +">"
        
        msgHtml = ""
        msgHtml = "<html><h1>Expired IOT Device Removal</h1>\n\n" + \
                    "<p>This is a system generated email. Do not reply to this email.</p>\n" + \
                    '<table border="1" cellpadding="1" cellspacing="1" style="width: 800px;">' + "\n" + \
                    "<caption>IOT Device Information</caption>\n" + \
                    "<thead>\n" + \
                    "<tr>\n" + \
                    ' <th scope="col">Owner</th>\n' + \
                    ' <th scope="col">Department</th>\n' + \
                    ' <th scope="col">Email</th>\n' + \
                    ' <th scope="col">Contact</th>\n' + \
                    ' <th scope="col">Location</th>\n' + \
                    ' <th scope="col">Name</th>\n' + \
                    ' <th scope="col">MAC Address</th>\n' + \
                    ' <th scope="col">IP Address</th>\n' + \
                    ' <th scope="col">Registration</th>\n' + \
                    ' <th scope="col">Expired Date</th>\n' + \
                    "</tr>\n" + \
                    "</thead>\n" + \
                    "<tbody>\n "

        # Process the list of email addresses
        for iot in iotInfo:
            # Only process if the email address matches
            iotProperties = iot.get_properties()
            if email in iotProperties['email']:
                if 'To' not in msg:
                    msg['To'] = iotProperties['owner'] + " <" + email +">"

                # Extract the dates from dictionary
                regDate = datetime.strptime(iotProperties['registration'], "%Y-%m-%d %H:%M:%S")
                expDate = datetime.strptime(iotProperties['expire'], "%Y-%m-%d %H:%M:%S")
                
                msgHtml += "<tr>\n" + \
                                "<td>%s</td>\n" % iotProperties['owner'] + \
                                "<td>%s</td>\n" % iotProperties['department'] + \
                                "<td>%s</td>\n" % iotProperties['email'] + \
                                "<td>%s</td>\n" % iotProperties['phone'] + \
                                "<td>%s</td>\n" % iotProperties['location'] + \
                                "<td>%s</td>\n" % iotProperties['iotname'] + \
                                "<td>%s</td>\n" % iot['name'].replace('-', ':') + \
                                "<td>%s</td>\n" % iotProperties['ipaddress'] + \
                                '<td><span style="color: rgb(0, 0, 0); font-family: Arial, Verdana, Helvetica, sans-serif; font-size: 11px;">%s</span></td>' % regDate.strftime("%b %d, %Y %H:%M:%S") + "\n" + \
                                '<td><span style="color: rgb(0, 0, 0); font-family: Arial, Verdana, Helvetica, sans-serif; font-size: 11px;">%s</span></td>' % expDate.strftime("%b %d, %Y %H:%M:%S") + "\n" + \
                                "</tr>\n"

        msgHtml += "</tbody>\n" + \
                    "</table>\n<br>\n<br>" + \
                    "\n<p>Should you encounter any issue, please contact IT HelpDesk (%s)</p>\n</html>" % helpdeskemail

        # Attach email for User
        msg.attach(MIMEText(msgHtml, 'html'))

        # Send email to User
        sendMail(mailSettings['mailhost'], sender, email, msg.as_string())
        LOGGER.info("(sendUserNotifyMail) Email sent to user: %s" % email)

    # Completed processing all expired devices and users notified
    LOGGER.info("(sendUserNotifyMail) Email sent to user completed")


def updateTagExpiredDevice(iotTag):
    """ Update Tag object information with expireState as True, to define IoT device as expired """
    LOGGER.info("(updateTag) Updating tag information with IoT Device Information: " + str(iotTag))
    try:
        iotTag.set_property('expireState','true')
        iotTag.update()
        LOGGER.info("(updateTag) Successfully updated tag: " + str(iotTag))
        return True
    except Exception as err:
        LOGGER.error("(updateTag) Unable to update tag:" + str(iotTag) + " Error:" + str(err))
        return False


def check_iot_expiration():
    """ Check for IoT devices which expiration date has elasped the current date and time for de-registration """
    global LOGGER
    LOGGER = g.user.logger

    LOGGER.info("IoT Expiration Check - started: " + str(datetime.now()))
    try:
        BAMCONFIG, IOTSETTINGS, MAILSETTINGS, CLEARPASS = readConfigFile(CONFIG_FILE)
    except Exception as err:
        raise Exception("(main) Configuration file error: " + str(err))
    
    bam = g.user.get_api()
    
    # Get Configuration Id
    LOGGER.info("(main) Getting configuration Id: " + str(BAMCONFIG['configuration']))
    bam_configuration = bam.get_configuration(BAMCONFIG['configuration'])

    # Get Tag Group Id
    LOGGER.info("(main) Getting Tag Group: " + str(BAMCONFIG['taggroup']))
    tag_group = bam.get_tag_group_by_name(BAMCONFIG['taggroup'])

    # Get list of Tags from Tag Group
    LOGGER.info("(main) Obtaining list of tags")
    tagEntities = tag_group.get_tags()

    # Store current date and time
    currentDateTime = datetime.now()
    LOGGER.info("(main) Current Date and Time: " + str(currentDateTime))

    # Extract information out and compare expiration date with current date and time
    expiredEntities = [] 
    for tag in tagEntities:
        LOGGER.info("(main) Checking tag name: " + str(tag.get_name()) + " with Id: " + str(tag.get_id()))
        tagProperties = tag.get_properties()

        # Check expireState in tag
        # If false, check whether it has reached expiration date
        # If true, check whether IP address has been de-allocated
        if "false" in tagProperties['expireState']:
            # Format: expire=2019-09-21 23:59:59.0
            # Discard last 2 characters ".0" which was added from BAM
            #MN#tagProperties['expire'] = tagProperties['expire'][:len(tagProperties['expire'])-2]
            expireDateTime = datetime.strptime(tagProperties['expire'], '%Y-%m-%d %H:%M:%S')
            
            # Compare current date and time with expiration date and time on tag
            # If expired, change expireState to true
            # If valid, ignore
            if expireDateTime < currentDateTime:
                LOGGER.info("(main) IoT Device: " + str(tag.get_name()) + " has reached expiration: " + str(expireDateTime) + ". Will be removed from DHCP.")
              # Format: u'properties': u'expireState=false|ipaddress=172.16.0.2|registration=2018-10-12 16:16:27.0|expire=2019-09-21 23:59:59.0|email=sysadmin2@acme.corp|'
                tag.set_properties(tagProperties)
                expiredEntities.append(tag)
        
        # For those which has expired, just double confirm the addresses are not allocated
        else:
            LOGGER.info("(main) Checking Address Allocation for IP: " + str(tagProperties['ipaddress']))
            try:
                bam_configuration.get_ip4_address(tagProperties['ipaddress']) # discard result
                LOGGER.warn("(main) Address still allocated for this IoT Device which has an expired state. Adding into list of expired devices")
                expiredEntities.append(tag)
            except bluecat.api_exception.PortalException: # ip address not found
                pass
    
    ###### Completed Analysis ######
    if len(expiredEntities) != 0:
        LOGGER.info("(main) IoT Device analysis complete. Processing expired IoT Devices and removing from DHCP Allocation")

    #####################################################################
    # Aruba Clearpass portion, to add MAC Address for MAC Authentication
        LOGGER.info("(main) Initializing Aruba Clearpass settings")
        if CLEARPASS['apihost']:
            apiclient = cpGetClient(CLEARPASS['apihost'], DEBUG, CLEARPASS['client_id'], CLEARPASS['client_secret'])
        else:
            apiclient = None

    ###### Start Processing of Expired IoT Devices #######
      # 1. remove IP address allocation
      # 2. update tag
        for tag in expiredEntities:
            tagProperties = tag.get_properties()
            LOGGER.info("(main) Obtaining IP Address information: " + tagProperties['ipaddress'])
            try:
                ipAddressEntity = bam_configuration.get_ip4_address(tagProperties['ipaddress'])
            except PortalError: # ip address not found
                LOGGER.info("(main) IP Address not assigned")
                ipAddressEntity = None

            if ipAddressEntity:
                LOGGER.info("(main) Deleting IP Address allocation: " + str(ipAddressEntity.get_id()))
                ipAddressEntity.delete()

            LOGGER.info("(main) Updating Tag containing IoT Device information: " + str(tag.get_name()))  
            updateTagExpiredDevice(tag)

            LOGGER.info("(main) Deleting MAC Address from Aruba Clearpass")
            macAddress = tag.get_name()
            if apiclient:
                cpDelMac(apiclient, removeMacChars(macAddress))
            LOGGER.debug("(main->cpDelMac) MAC address deleted from Aruba Clearpass: " + str(macAddress))

        LOGGER.debug("(main) " + str(expiredEntities))

        LOGGER.info("(main) Proceeding to deploy DDS with updated information")
        deployServerServices(bam_configuration, BAMCONFIG['ddServers'])

        ###### Completed Processing Expired IoT Devices #######
        LOGGER.info("(main) Completed processing all expired IoT Devices")
    
        ###### Notify Administrator on Device Removal #######
        sendAdminNotifyMail(MAILSETTINGS, expiredEntities)

        ###### Notify Device Owner on Device Removal #######
        sendUserNotifyMail(MAILSETTINGS, expiredEntities)

    else:
        LOGGER.info("(main) IoT Device analysis complete. No expired IoT Devices to be processed.") 


# RELEASE NOTES
# v1.0 - 20190225 - Added Aruba Clearpass section to delete MAC Address from the NAC
#
