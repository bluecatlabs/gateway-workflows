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
# Description: Bulk Register IP Address Page

# Various Flask framework items.
import os
import sys

from flask import url_for, redirect, render_template, flash, g, request, jsonify

from bluecat import route, util
import config.default_config as config
from main_app import app

from .bulk_register_ip_address_form import get_resource_text
from .bulk_register_ip_address_form import GenericFormTemplate

def get_configuration(api, config_name):
    configuration = api.get_configuration(config_name)
    return configuration

def register_by_api(api, ip_address_list):
    configuration = get_configuration(api, config.default_configuration)
    for line in ip_address_list:
        address = line[0]
        name = line[1]
        mac_address = line[2]
        comments = line[3]
        
        try:
            ip_address = configuration.get_ip4_address(address)
            if 0 < len(name):
                ip_address.set_name(name)
            if 0 < len(mac_address):
                ip_address.set_property('macAddress', mac_address)
            if 0 < len(comments):
                ip_address.set_property('Comments', comments)
            ip_address.update()
                
        except Exception as e:
            properties = ''
            if 0 < len(name):
                properties = 'name=' + name
            if 0 < len(comments):
                properties += '|Comments=' + comments
            ip_address = configuration.assign_ip4_address(address, mac_address, '', 'MAKE_STATIC', properties)

# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/bulk_register_ip_address/bulk_register_ip_address_endpoint', methods=['GET', 'POST'])
@util.workflow_permission_required('bulk_register_ip_address_page')
@util.exception_catcher
def bulk_register_ip_address_bulk_register_ip_address_page():
    form = GenericFormTemplate()
    return render_template(
        'bulk_register_ip_address_page.html',
        form=form,
        text=get_resource_text(),
        options=g.user.get_options(),
    )

@route(app, '/bulk_register_ip_address/submit_bulk_ip_address_list', methods=['POST'])
@util.workflow_permission_required('bulk_register_ip_address_page')
@util.exception_catcher
def bulk_register_ip_address_bulk_register_ip_address_page_submit_bulk_ip_address_list():
    ip_address_list = request.get_json()  
    register_by_api(g.user.get_api(), ip_address_list)

    text=get_resource_text()
    g.user.logger.info('SUCCESS')
    flash(text['success'], 'succeed')
    return jsonify('', 200)
