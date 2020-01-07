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

import sys, os, re, json, csv, time, logging, traceback, smtplib
from flask import g
import bluecat.api
from bluecat.bdds_server import Server
from . import clearpass
from configparser import ConfigParser
from datetime import datetime
from datetime import timedelta

FORMATTER = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")

def readConfigFile(filename):
    """ Read the configuration file iotipallocation.conf and store content as dictionary
    
        BAMOBJECT: contains the BlueCat Address Manager host information and API Client credentials
        BAMCONFIG: contains BlueCat Address Manager objects such as configuration name, network and blocks
                   tag objects and DNS & DHCP Server name
        IOTSETTINGS: the default registration period in number of days before expiration
        MAILSETTINGS: settings for sending out notification emails
        CLEARPASS: Aruba Clearpass settings containing the host, client name, key, description and attributes for the IoT Devices
    """
    LOGGER = g.user.logger
    try:
        LOGGER.info("Reading configuration file: " + filename)
        parser = ConfigParser()
        parser.read(filename)

        ## BAMCONFIG
        BAMCONFIG = {}
        BAMCONFIG['configuration'] = parser.get('BAMCONFIG', 'configuration')
        LOGGER.debug("(readConfigFile) BAM Configuration retrieved: " + BAMCONFIG['configuration'])

        networks = []
        for network in parser.get('BAMCONFIG', 'networks').split(','):
            networks.append(network)
        LOGGER.debug("(readConfigFile) IoT network information retrieved: " + str(networks))

        locations = []
        for location in parser.get('BAMCONFIG', 'locations').split(','):
            locations.append(location)
        LOGGER.debug("(readConfigFile) Location information retrieved: " + str(locations))

        netloc = {}
        netloc = dict(zip(locations, networks))
        BAMCONFIG['netloc'] = netloc
        LOGGER.debug("(readConfigFile) Location and network information mapped: " + str(BAMCONFIG['netloc']))

        BAMCONFIG['taggroup'] = parser.get('BAMCONFIG', 'taggroup')
        LOGGER.debug("(readConfigFile) Tag Group name retrieved: " + BAMCONFIG['taggroup'])
       
        BAMCONFIG['iotview'] = parser.get('BAMCONFIG', 'iotview')
        LOGGER.debug("(readConfigFile) IoT DNS View retrieved: " + BAMCONFIG['iotview'])

        BAMCONFIG['iotdomain'] = parser.get('BAMCONFIG', 'iotdomain')
        LOGGER.debug("(readConfigFile) IoT Domain retrieved: " + BAMCONFIG['iotdomain'])

        ddServers = []
        for ddServer in parser.get('BAMCONFIG', 'ddservers').split(','):
            ddServers.append(ddServer)
        BAMCONFIG['ddServers'] = ddServers
        LOGGER.debug("(readConfigFile) BlueCat DDS names retrieved: " + str(BAMCONFIG['ddServers']))

    
        ## IOT SETTINGS
        IOTSETTINGS = {}
        IOTSETTINGS['expire'] = parser.get('IOTSETTINGS', 'expire')
        LOGGER.debug("(readConfigFile) IOT expire period setting retrieved: " + IOTSETTINGS['expire'])
        IOTSETTINGS['expire'] = int(IOTSETTINGS['expire'])
    
    
        ## EMAIL
        MAILSETTINGS = {}
        MAILSETTINGS['mailhost'] = parser.get('MAILSETTINGS', 'mailhost')
        LOGGER.debug("(readConfigFile) Mail host setting retrieved: " + MAILSETTINGS['mailhost'])

        MAILSETTINGS['mailuser'] = parser.get('MAILSETTINGS', 'mailuser')
        LOGGER.debug("(readConfigFile) Mail user name retrieved: " + MAILSETTINGS['mailuser'])

        MAILSETTINGS['mailpass'] = parser.get('MAILSETTINGS', 'mailpass')
        LOGGER.debug("(readConfigFile) Mail password retrieved")
        
        MAILSETTINGS['maildomain'] = parser.get('MAILSETTINGS', 'maildomain')
        LOGGER.debug("(readConfigFile) Mail domain retrieved: " + MAILSETTINGS['maildomain'])

        if "true" in parser.get("MAILSETTINGS", 'ssl'):
            MAILSETTINGS['ssl'] = True
        else:
            MAILSETTINGS['ssl'] = False
        LOGGER.debug("(readConfigFile) Mail ssl settings retrived: " + str(MAILSETTINGS['ssl']))

        ## CLEARPASS
        CLEARPASS = {}
        CLEARPASS['client_id'] = parser.get('CLEARPASS', 'client_id')
        LOGGER.debug("(readConfigFile) Clearpass client id retrieved")
        
        CLEARPASS['client_secret'] = parser.get('CLEARPASS', 'client_secret')
        LOGGER.debug("(readConfigFile) Clearpass client secret retrieved")
        
        CLEARPASS['grant_type'] = parser.get('CLEARPASS', 'grant_type')
        LOGGER.debug("(readConfigFile) Clearpass client grant type retrieved")
        
        CLEARPASS['apihost'] = parser.get('CLEARPASS', 'apihost')
        LOGGER.debug("(readConfigFile) Clearpass API Host retrieved: " + str(CLEARPASS['apihost']))
    
        CLEARPASS['description'] = parser.get('CLEARPASS', 'description')
        LOGGER.debug("(readConfigFile) Clearpass description retrieved: " + str(CLEARPASS['description']))
    
        attributes = parser.get('CLEARPASS', 'attributes')
        CLEARPASS['attributes'] = json.loads(attributes)
        LOGGER.debug("(readConfigFile) Clearpass attributes retrieved: " + str(CLEARPASS['attributes']))
      
    except Exception as err:
        LOGGER.error(err)
        LOGGER.error("Please check configuration file: " + filename)
        raise err

    return BAMCONFIG, IOTSETTINGS, MAILSETTINGS, CLEARPASS


def sendMail(mailhost, sender, recipient, message):
    """ Specifically perform sending of mail to SMTP server """
    LOGGER = g.user.logger
    try:
        smtpObj = smtplib.SMTP(mailhost)
        smtpObj = smtpObj.sendmail(sender, recipient, message)
        LOGGER.info("(sendMail) Successfully delivered mail to recipient")
    except Exception as err:
        LOGGER.warning("(sendMail) Problem delivering email to: " + str(recipient) + " via" + str(mailhost) + " Error: " + str(err))


def isInteger(s):
    """ Returns True if a string contains an Integer, False otherwise """
    try:
        int(s)
        return True
    except ValueError:
        return False


def deployServerServices(configuration, ddServerNames):
    """ Perform DNS & DHCP server DHCP deployment to push DHCP Reserved IP address for IoT Devices"""
    LOGGER = g.user.logger
    if len(ddServerNames) == 0:
        LOGGER.warning("(deployServerServices) No DD Server name defined in array: " + str(ddServerNames))
        return False

    ddServerEntities = []

    for ddServerName in ddServerNames:
        LOGGER.info("(deployServerServices) Getting Server name: " + ddServerName)
        ddServerEntities.append(configuration.get_server(ddServerName))
   
    for ddServer in ddServerEntities:
        LOGGER.info("(deployServerServices) Deploying Server with Id: " + str(ddServer.get_id()))
        ddServer.deploy_services(['DNS','DHCP'])

    LOGGER.info("(deployServerServices) All server deployments queued.")

    # Once deployed, monitor the status of the deployment to make sure it is successful
    LOGGER.info("(checkServerDeploymentStatus) Servers: " + str(ddServerEntities))
    errorEncountered = False
    for server in ddServerEntities:
        LOGGER.info("(checkServerDeploymentStatus) Please wait while changes are being deployed to server: " + str(server))
                                   
        while (True):
            LOGGER.info("Checking server deployment status")
            status = server.get_server_deployment_status()
                                                                 
            if status == Server.DONE:
                LOGGER.info("Done!")
                break
            elif status == Server.EXECUTING:
                LOGGER.info("Executing...")
            elif status == Server.INITIALIZING:
                LOGGER.info("Initializing...")
            elif status == Server.QUEUED:
                LOGGER.info("Queued...")
            elif status == Server.CANCELLING:
                LOGGER.info("Cancelling...")
            else:
                errorEncounted = True
                if status == Server.NO_RECENT_DEPLOYMENT:
                    LOGGER.warning("No recent deployment")
                elif status == Server.CANCELLED:
                    LOGGER.warning("Cancelled")
                elif status == Server.FAILED:
                    LOGGER.error("Failed")
                elif status == Server.NOT_DEPLOYED:
                    LOGGER.warning("Not Deployed")
                elif status == Server.WARNING:
                    LOGGER.warning("Warning")
                elif status == Server.INVALID:
                    LOGGER.error("Invalid")
                else:
                    LOGGER.error("Unknown status: " + str(status))
                break
            time.sleep(1)
            
        LOGGER.info("(checkServerDeploymentStatus) Server deployment completed: " + str(server))

    if not errorEncountered:
        LOGGER.info("(checkServerDeploymentStatus) All deployment completed successfully")
        return True
    else:
        LOGGER.info("(checkServerDeploymentStatus) Server deployment unsuccessful! Please check event logs in BAM")
        return False


def cpGetClient(apihost, debug, client_id, client_secret):
    """ Return Aruba Clearpass client object session for making API calls """
    return clearpass.Client(
        host = apihost, timeout = 60, insecure = True, verbose = True, debug = debug,
        access_token = None, client_id = client_id, client_secret = client_secret)


def cpAddMac(clearpassObj, endpointObj):
    """ Aruba Clearpass method to add Mac Address for network access """
    return clearpassObj.post("/endpoint", endpointObj)


def cpGetMac(clearpassObj, macAddress):
    """ Aruba Clearpass method to get Mac Address """
    return clearpassObj.get("/endpoint/mac-address/" + macAddress)
    
  
def cpDelMac(clearpassObj, macAddress):
    """ Aruba Clearpass method to delete Mac Address for blocking network access """
    return clearpassObj.delete("/endpoint/mac-address/" + macAddress)
