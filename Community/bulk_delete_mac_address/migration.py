# Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates
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
# Date: 2020-12-15
# Gateway Version: 20.12.1
# Description: Bulk Delete MAC Address Migration

from bluecat.api_exception import PortalException

def get_mac_address(configuration, address):
    mac_addr = None
    try:
        mac_addr = configuration.get_mac_address(address)
    except PortalException:
        pass
    return mac_addr


def delete_mac_address(configuration, address):
    mac_address = get_mac_address(configuration, address)
    if mac_address is not None:
        print('MAC Address %s is in configuration(%s)' % (address, configuration.get_name()))
        try:
            linked_ip_address_obj_list = list(mac_address.get_linked_entities(mac_address.IP4Address))
            if linked_ip_address_obj_list == []:
                print(f'MAC Address {address} has no linked IP Address')
                mac_address.delete()
            else:
                ip_addresses = ''
                for i, item in enumerate(linked_ip_address_obj_list):
                    ip_address = item.get_address()
                    if len(linked_ip_address_obj_list) -1 == i:
                        ip_addresses += ip_address
                    else:
                        ip_addresses += ip_address + ', '
                print(f'MAC Address {address} has IP Addresses {ip_addresses} linked. Deletion aborted for this MAC Address')
        except PortalException:
            pass
    else:
        print('MAC Address %s is NOT in configuration(%s)' % (address, configuration.get_name()))

