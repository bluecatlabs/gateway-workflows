# Copyright 2022 BlueCat Networks (USA) Inc. and its affiliates
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
# Date: 2022-06-09
# Gateway Version: 21.11.2
# Description: Bulk Register DHCP Range Page

import csv
import os

from flask import url_for, redirect, render_template, flash, g, request, jsonify

from bluecat import route, util
import config.default_config as config
from main_app import app

from .bulk_register_dhcp_range_form import get_resource_text
from .bulk_register_dhcp_range_form import GenericFormTemplate

from .bulk_register_dhcp_range import add_dhcp_ranges

TEMP_CSV_FILE = 'tmp.csv'

def module_path():
    return os.path.dirname(os.path.abspath(__file__))

def get_configuration(api, config_name):
    configuration = api.get_configuration(config_name)
    return configuration

def load_dhcp_ranges(file_buf):
    file_path = os.path.join(module_path(), TEMP_CSV_FILE)
    file_buf.save(file_path)
    dhcp_ranges = []
    with open(file_path) as csvfile:
        for row in csv.DictReader(csvfile):
            dhcp_ranges.append(row)
    os.remove(file_path)
    return dhcp_ranges

# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/bulk_register_dhcp_range/bulk_register_dhcp_range_endpoint', methods=['GET', 'POST'])
@util.workflow_permission_required('bulk_register_dhcp_range_page')
@util.exception_catcher
def bulk_register_dhcp_range_bulk_register_dhcp_range_page():
    form = GenericFormTemplate()
    return render_template(
        'bulk_register_dhcp_range_page.html',
        form=form,
        text=get_resource_text(),
        options=g.user.get_options(),
    )

@route(app, '/bulk_register_dhcp_range/form', methods=['POST'])
@util.workflow_permission_required('bulk_register_dhcp_range_page')
@util.exception_catcher
def bulk_register_dhcp_range_bulk_register_dhcp_range_page_form():
    print('/bulk_register_dhcp_range/form is called')
    form = GenericFormTemplate()
    text=get_resource_text()
    dhcp_ranges = load_dhcp_ranges(form.file.data)
    if 0 < len(dhcp_ranges):
        api = g.user.get_api()
        configuration = api.get_configuration(config.default_configuration)
        shard_network_id = configuration.get_property('sharedNetwork')
        if shard_network_id is None:
            shard_network_id = '0'
        add_dhcp_ranges(api.spec_api, configuration.get_id(), int(shard_network_id), dhcp_ranges)
    
    # Put form processing code here
    g.user.logger.info('SUCCESS')
    flash(text['success'], 'succeed')
    return redirect(url_for('bulk_register_dhcp_rangebulk_register_dhcp_range_bulk_register_dhcp_range_page'))
