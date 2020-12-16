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
from suds import WebFault
from urllib.parse import urlparse

from bluecat import route, tag, util
from bluecat.entity import Entity
from bluecat.api_exception import BAMException, PortalException
from bluecat.internal.wrappers.generic_getters import get_entity_by_name
from bluecat_portal import config
from bluecat.util import safe_str

from main_app import app

def get_mac_address(configuration, address):
    mac_addr = None
    try:
        mac_addr = configuration.get_mac_address(address)
    except PortalException:
        pass
    return mac_addr

def get_mac_pool(configuration, mac_pool_name):
    mac_pool = None
    try:
        mac_pool = configuration.get_child_by_name(mac_pool_name, configuration.MACPool)
    except PortalException as e:
        print('MAC Pool %s is not in configuration(%s).' % (mac_pool_name, configuration.get_name()))
    return mac_pool

def normalize_date_format(date_str):
    return date_str.replace('/', '-')

def register_mac_address(configuration, address, asset_code, mac_pool, comments):
    mac_address = get_mac_address(configuration, address)
    mac_pool_entity = get_mac_pool(configuration, mac_pool)
    if mac_address is not None:
        print('MAC Address %s is in configuration(%s)' % (address, configuration.get_name()))
        if asset_code != '':
            mac_address.set_name(asset_code)
            mac_address.set_property('Comments', comments)
            mac_address.update()
        if mac_pool != '' and mac_pool_entity is not None:
            mac_address.set_mac_pool(mac_pool_entity)
    else:
        print('MAC Address %s is NOT in configuration(%s)' % (address, configuration.get_name()))
        properties = 'Comments=' + comments
        mac_address = configuration.add_mac_address(address, asset_code, mac_pool_entity, properties)

