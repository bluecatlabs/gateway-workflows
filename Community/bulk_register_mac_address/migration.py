# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates
# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By: BlueCat Networks
# Date: 2019-03-14
# Gateway Version: 18.10.2
# Description: Bulk Register MAC Address Migration

# Various Flask framework items.
import codecs
import datetime
import os
import sys

from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
from suds import WebFault
from urllib.parse import urlparse
from xml.dom.minidom import parse

from bluecat import route, tag, util
from bluecat.entity import Entity
from bluecat.api_exception import BAMException, PortalException
from bluecat_portal import config
from main_app import app

def create_udf_node(dom, attribute, value):
    child = dom.createElement('value')
    child.setAttribute('name', attribute)
    child.setAttribute('data', value)
    return child

def get_udf_value(node, attribute):
    for child in node.childNodes:
        if child.nodeType == child.ELEMENT_NODE:
            if child.tagName == 'value':
                if child.getAttribute('name') == attribute:
                    return child.getAttribute('data')
    return ''
    
def construct_xml(workflow_dir, mac_address_list):
    dom = parse(workflow_dir + '/templates/' + 'config.xml')
    elm_config = dom.getElementsByTagName('configuration')[0]
    elm_config.setAttribute('name', config.default_configuration)
    
    for line in mac_address_list:
        child = dom.createElement('mac')
        child.setAttribute('address', str(line[1]))
        child.appendChild(create_udf_node(dom, 'AssetCode', str(line[0])))
        child.appendChild(create_udf_node(dom, 'EmployeeCode', str(line[2])))
        child.appendChild(create_udf_node(dom, 'UpdateDate', normalize_date_format(line[3])))
        elm_config.appendChild(child)
    return dom
    
def store_xml(workflow_dir, dom):
    f = open(workflow_dir + '/temporary.xml', 'w', encoding='utf-8')
    f.write(dom.toprettyxml())
    f.close()

def get_mac_address(configuration, address):
    mac_addr = None
    try:
        mac_addr = configuration.get_mac_address(address)
    except PortalException:
        pass
    return mac_addr

def get_mac_address(configuration, address):
    mac_addr = None
    try:
        mac_addr = configuration.get_mac_address(address)
    except PortalException:
        pass
    return mac_addr
    
def normalize_date_format(date_str):
    return date_str.replace('/', '-')

def register_mac_address(configuration, address, asset_code, employee_code, update_date):
    mac_address = get_mac_address(configuration, address)
    if mac_address is not None:
        print('MAC Address %s is in configuration(%s)' % (address, configuration.get_name()))
    else:
        print('MAC Address %s is NOT in configuration(%s)' % (address, configuration.get_name()))
        print('update_date = %s' % str(update_date))
        mac_address = configuration.add_mac_address(address)
    mac_address.set_property('AssetCode', asset_code)
    mac_address.set_property('EmployeeCode', employee_code)
    mac_address.set_property('UpdateDate', normalize_date_format(update_date))
    mac_address.update()

def upload_migration_xml(api, workflow_dir, filename):
    hostname = urlparse(api.get_url()).hostname
    print('Hostname: %s' % hostname)
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(hostname, username='root', password='root')
    
    scp = SCPClient(ssh.get_transport())
    scp.put(workflow_dir + '/' + filename, '/data/migration/incoming/')
    
def migrate_xml(api, workflow_dir):
    upload_migration_xml(api, workflow_dir, 'temporary.xml')
    try:
        api._api_client.service.migrateFile('temporary.xml')
    except WebFault as e:
        raise BAMException(str(e))        
    return
