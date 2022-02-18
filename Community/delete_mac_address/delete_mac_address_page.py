# Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
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
# Date: 2021-10-10
# Gateway Version: 18.10.2
# Description: Delete MAC Address Page

# Various Flask framework items.
from flask import url_for, redirect, render_template, flash, g

from bluecat import route, util
from bluecat.entity import Entity
from bluecat.api_exception import PortalException

import config.default_config as config
from main_app import app

from .delete_mac_address_form import get_resource_text
from .delete_mac_address_form import GenericFormTemplate

def get_configuration():
    configuration = None
    if g.user:
        configuration = g.user.get_api().get_configuration(config.default_configuration)
    return configuration
def get_mac_address(configuration, address):
    mac_addr = None
    try:
        mac_addr = configuration.get_mac_address(address)
    except PortalException:
        pass
    return mac_addr

def delete_mac_address(configuration, address, text):
    mac_address = get_mac_address(configuration, address)
    if mac_address is not None:
        #print('MAC Address %s is in configuration(%s)' % (address, configuration.get_name()))
        try:
            linked_ip_address_obj_list = list(mac_address.get_linked_entities(mac_address.IP4Address))
            if linked_ip_address_obj_list == []:
                flash(address + text['deleted'], 'succeed')
                #print(f'MAC Address {address} has no linked IP Address')
                mac_address.delete()
            else:
                ip_addresses = ''
                for i, item in enumerate(linked_ip_address_obj_list):
                    ip_address = item.get_address()
                    if len(linked_ip_address_obj_list) -1 == i:
                        ip_addresses += ip_address
                    else:
                        ip_addresses += ip_address + ', '
                flash(text['aborted'], 'failed')
                flash(f'MAC Address {address} <=> IP Addresses {ip_addresses}', 'failed')
                #print(f'MAC Address {address} has IP Addresses {ip_addresses} linked. Deletion aborted for this MAC Address')
        except PortalException:
            pass
    else:
        flash(address + text['noregistered'], 'failed')
        print('MAC Address %s is NOT in configuration(%s)' % (address, configuration.get_name()))



# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/delete_mac_address/delete_mac_address_endpoint')
@util.workflow_permission_required('delete_mac_address_page')
@util.exception_catcher
def delete_mac_address_delete_mac_address_page():
    form = GenericFormTemplate()
    configuration = get_configuration()
    #form.mac_pool.choices = get_mac_pools(configuration)
    return render_template(
       'delete_mac_address_page.html',
       form=form,
       text=get_resource_text(),
       options=g.user.get_options(),
    )

@route(app, '/delete_mac_address/form', methods=['POST'])
@util.workflow_permission_required('delete_mac_address_page')
@util.exception_catcher
def delete_mac_address_delete_mac_address_page_form():
    form = GenericFormTemplate()
    configuration = get_configuration()
    text = get_resource_text()
    if form.validate_on_submit():
        mac_address = get_mac_address(configuration, form.mac_address.data)
        #asset_code = form.asset_code.data
        delete_mac_address(configuration, form.mac_address.data, text)

        # Put form processing code here
        g.user.logger.info('SUCCESS')
        # flash(text['success'], 'succeed')
        return redirect(url_for('delete_mac_addressdelete_mac_address_delete_mac_address_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'delete_mac_address_page.html',
            form=form,
            text=text,
            options=g.user.get_options(),
        )
