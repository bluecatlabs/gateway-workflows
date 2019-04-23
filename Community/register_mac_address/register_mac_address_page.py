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
# Date: 2019-03-14
# Gateway Version: 18.10.2
# Description: Register MAC Address Page

# Various Flask framework items.
from flask import url_for, redirect, render_template, flash, g

from bluecat import route, util
from bluecat.entity import Entity
from bluecat.api_exception import PortalException

import config.default_config as config
from main_app import app

from .register_mac_address_form import get_resource_text
from .register_mac_address_form import GenericFormTemplate

def get_mac_pool(tag_id):
    mac_pool = None
    if g.user:
        tag = g.user.get_api().get_entity_by_id(tag_id)
        print('tag (%d) is found.' % tag.get_id())
        mac_pools = tag.get_linked_entities(Entity.MACPool)
        mac_pool = next(mac_pools, None)
        if mac_pool is None:
            print('MAC Pool is not found.')
    return mac_pool

def get_mac_address(configuration, address):
    mac_addr = None
    try:
        mac_addr = configuration.get_mac_address(address)
    except PortalException:
        pass
    return mac_addr

def get_configuration():
    configuration = None
    if g.user:
        configuration = g.user.get_api().get_configuration(config.default_configuration)
    return configuration
    
def get_tag_tree(base, tag):
    result = []
    if base != '':
        base += '.' + tag.get_name()
    else:
        base = tag.get_name()
        
    result.append((tag.get_id(), base))
    children = tag.get_tags()
    for c in children:
        result.extend(get_tag_tree(base, c))
    return result	

def get_device_groups():
    text=get_resource_text()
    device_groups = [
        (1, text['label_general_group']),
        (2, text['label_design_group']), 
        (3, text['label_production_group'])
    ]
    return device_groups
    
def get_locations():
    result = []
    if g.user:
        tag_group = g.user.get_api().get_tag_group_by_name('Locations')
        children = tag_group.get_tags()
        for c in children:
            result.extend(get_tag_tree('', c))
    return result


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/register_mac_address/register_mac_address_endpoint')
@util.workflow_permission_required('register_mac_address_page')
@util.exception_catcher
def register_mac_address_register_mac_address_page():
    form = GenericFormTemplate()
    form.device_group.choices = get_device_groups()
    form.location.choices = get_locations()
    return render_template(
        'register_mac_address_page.html',
        form=form,
        text=get_resource_text(),
        options=g.user.get_options(),
    )

@route(app, '/register_mac_address/form', methods=['POST'])
@util.workflow_permission_required('register_mac_address_page')
@util.exception_catcher
def register_mac_address_register_mac_address_page_form():
    form = GenericFormTemplate()
    form.device_group.choices = get_device_groups()
    form.location.choices = get_locations()    
    if form.validate_on_submit():
        configuration = get_configuration()
        if configuration is not None:
            mac_pool = get_mac_pool(form.location.data)
            if mac_pool is None:
                g.user.logger.info('Configuration Error, No MAC Pool is associated.')
                text = get_resource_text()
                flash(text['config_error'])
                return render_template('register_mac_address_page.html', form=form,
                                        text=text, options=g.user.get_options())

            mac_address = get_mac_address(configuration, form.mac_address.data)
            if mac_address is not None:
                print('MAC Address %s (%d) is in configuration' % (form.mac_address.data, mac_address.get_id()))
                mac_address.set_mac_pool(mac_pool)
            else:
                print('MAC Address %s is NOT in configuration' % form.mac_address.data)
                mac_address = configuration.add_mac_address(form.mac_address.data, '', mac_pool)
            mac_address.set_property('AssetCode', form.asset_code.data)
            mac_address.set_property('EmployeeCode', form.employee_code.data)
            mac_address.update()
        # Put form processing code here
        g.user.logger.info('SUCCESS')
        text = get_resource_text()
        flash(text['success'], 'succeed')
        return redirect(url_for('register_mac_addressregister_mac_address_register_mac_address_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'register_mac_address_page.html',
            form=form,
            text=get_resource_text(),
            options=g.user.get_options(),
        )
