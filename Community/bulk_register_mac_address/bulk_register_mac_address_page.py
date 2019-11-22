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
# Description: Bulk Register MAC Address Page

# Various Flask framework items.
import os
import sys
import json

from flask import request, url_for, redirect, render_template, flash, jsonify, g

from bluecat import route, util
import config.default_config as config
from main_app import app
from .bulk_register_mac_address_form import GenericFormTemplate

from .bulk_register_mac_address_form import module_path, get_resource_text
from .migration import register_mac_address, construct_xml, store_xml, migrate_xml

def get_configuration(api, config_name):
    configuration = api.get_configuration(config_name)
    return configuration

def register_by_xml(api, workflow_dir, mac_address_list):
    dom = construct_xml(workflow_dir, mac_address_list)
    store_xml(workflow_dir, dom)
    migrate_xml(api, workflow_dir)
    dom.unlink()

def register_by_api(api, mac_address_list):
    configuration = get_configuration(api, config.default_configuration)
    for line in mac_address_list:
        print(line)
        asset_code = str(line[0])
        address = str(line[1])
        employee_code = str(line[2])
        update_date = str(line[3])
        register_mac_address(configuration, address, asset_code, employee_code, update_date)
        

# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/bulk_register_mac_address/bulk_register_mac_address_endpoint', methods=['GET', 'POST'])
@util.workflow_permission_required('bulk_register_mac_address_page')
@util.exception_catcher
def bulk_register_mac_address_bulk_register_mac_address_page():
    form = GenericFormTemplate()
    return render_template(
        'bulk_register_mac_address_page.html',
        form=form,
        text=get_resource_text(),
        options=g.user.get_options(),
    )


@route(app, '/bulk_register_mac_address/submit_bulk_mac_address_list', methods=['POST'])
@util.workflow_permission_required('bulk_register_mac_address_page')
@util.exception_catcher
def bulk_register_mac_address_bulk_register_mac_address_page_submit_bulk_mac_address_list():
    mac_address_list = request.get_json()
    print('Size of mac_address_list %d' % len(mac_address_list))
    if len(mac_address_list) > 1000:
        register_by_xml(g.user.get_api(), module_path(), mac_address_list)
    else:
        register_by_api(g.user.get_api(), mac_address_list)

    text=get_resource_text()
    g.user.logger.info('SUCCESS')
    flash(text['success'], 'succeed')
    return jsonify('', 200)

