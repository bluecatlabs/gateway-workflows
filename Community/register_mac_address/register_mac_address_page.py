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
from .register_mac_address_form import UniqueNameValidator

def get_configuration():
    configuration = None
    if g.user:
        configuration = g.user.get_api().get_configuration(config.default_configuration)
    return configuration

def get_mac_pools(configuration):
    mac_pools = [(0, 'None')]
    try:
        children = configuration.get_children_of_type(configuration.MACPool)
        for child in children:
            mac_pools.append((child.get_id(), child.get_name()))
    except PortalException:
        pass
    return mac_pools

def get_mac_pool(configuration, mac_pool_id):
    mac_pool = None
    try:
        mac_pool = configuration._api.get_entity_by_id(mac_pool_id)
    except PortalException:
        pass
    return mac_pool

def get_mac_address(configuration, address):
    mac_addr = None
    try:
        mac_addr = configuration.get_mac_address(address)
    except PortalException:
        pass
    return mac_addr


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/register_mac_address/register_mac_address_endpoint')
@util.workflow_permission_required('register_mac_address_page')
@util.exception_catcher
def register_mac_address_register_mac_address_page():
    form = GenericFormTemplate()
    configuration = get_configuration()
    form.mac_pool.choices = get_mac_pools(configuration)
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
    configuration = get_configuration()
    form.mac_pool.choices = get_mac_pools(configuration)
    text = get_resource_text()
    mac_pool = get_mac_pool(configuration, form.mac_pool.data)
    if (mac_pool is not None) and (form.unique_check.data):
        validator = UniqueNameValidator(
            message=text['exist_message'],
            mac_addresses=mac_pool.get_linked_entities(Entity.MACAddress)
        )
        form.asset_code.validators.append(validator)
    if form.validate_on_submit():
        mac_address = get_mac_address(configuration, form.mac_address.data)
        asset_code = form.asset_code.data
        if mac_address is not None:
            print('MAC Address %s (%d) is in configuration' % (form.mac_address.data, mac_address.get_id()))
            if asset_code != '':
                mac_address.set_name(asset_code)
                mac_address.set_property('Comments', form.comments.data)
                mac_address.update()
            mac_address.set_mac_pool(mac_pool)
        else:
            print('MAC Address %s is NOT in configuration' % form.mac_address.data)
            properties = 'Comments=' + form.comments.data
            mac_address = \
                configuration.add_mac_address(form.mac_address.data, asset_code, mac_pool, properties)
        # Put form processing code here
        g.user.logger.info('SUCCESS')
        flash(text['success'], 'succeed')
        return redirect(url_for('register_mac_addressregister_mac_address_register_mac_address_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'register_mac_address_page.html',
            form=form,
            text=text,
            options=g.user.get_options(),
        )
