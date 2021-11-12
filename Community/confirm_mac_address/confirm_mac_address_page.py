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
# Date: 2021-11-10
# Gateway Version: 18.10.2
# Description: Confirm MAC Address Page

# Various Flask framework items.
from flask import url_for, redirect, render_template, flash, g

from bluecat import route, util
from bluecat.entity import Entity
from bluecat.api_exception import PortalException

import config.default_config as config
from main_app import app

from .confirm_mac_address_form import get_resource_text
from .confirm_mac_address_form import GenericFormTemplate

def get_configuration():
    configuration = None
    if g.user:
        configuration = g.user.get_api().get_configuration(config.default_configuration)
    return configuration

def get_mac_address(configuration, address):
    mac_addr = None
    try:
        mac_addr = configuration.get_mac_address(address)
        print(mac_addr)
    except PortalException:
        pass
    return mac_addr


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/confirm_mac_address/confirm_mac_address_endpoint')
@util.workflow_permission_required('confirm_mac_address_page')
@util.exception_catcher
def confirm_mac_address_confirm_mac_address_page():
    form = GenericFormTemplate()
    configuration = get_configuration()
    return render_template(
       'confirm_mac_address_page.html',
       form=form,
       text=get_resource_text(),
       options=g.user.get_options(),
    )

@route(app, '/confirm_mac_address/form', methods=['POST'])
@util.workflow_permission_required('confirm_mac_address_page')
@util.exception_catcher
def confirm_mac_address_confirm_mac_address_page_form():
    form = GenericFormTemplate()
    configuration = get_configuration()
    text = get_resource_text()
    
    if form.validate_on_submit():
        mac_address = get_mac_address(configuration, form.mac_address.data)
        if mac_address is not None:
            mac_pool=mac_address.get_property('macPool')
            if mac_pool is None:
                mac_pool=text['nomacpool']
            flash(mac_address.get_address() + text['registered'] , 'succeed')
            flash('MAC Pool : ' + mac_pool, 'succeed')
        else:
            flash(form.mac_address.data + text['noregistered'], 'failed')
            
        # Put form processing code here
        g.user.logger.info('SUCCESS')
        return redirect(url_for('confirm_mac_addressconfirm_mac_address_confirm_mac_address_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'confirm_mac_address_page.html',
            form=form,
            text=text,
            options=g.user.get_options(),
        )
