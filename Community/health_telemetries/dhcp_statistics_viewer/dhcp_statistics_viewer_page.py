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
# By: BlueCat Networks Inc.
# Date: 2022-05-01
# Gateway Version: 21.11.2
# Description: Health Telemetry DHCP Statistics Viewer Page.py

import os
import sys
import codecs
import json
from datetime import datetime, timedelta
import traceback

from flask import request, url_for, redirect, render_template, flash, g, jsonify

from bluecat import route, util
from bluecat.wtform_extensions import GatewayForm


import config.default_config as config
from main_app import app

from ..health_telemetries.telemetry_buffer import TelemetryBuffer

def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))

def get_resource_text():
    return util.get_text(module_path(), config.language)

def get_configuration():
    configuration = None
    if g.user:
        configuration = g.user.get_api().get_configuration(config.default_configuration)
    return configuration
    
class GenericFormTemplate(GatewayForm):
    workflow_name = 'dhcp_statistics_viewer'
    workflow_permission = 'dhcp_statistics_viewer_page'
    
# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/dhcp_statistics_viewer/load_col_model')
@util.workflow_permission_required('dhcp_statistics_viewer_page')
@util.exception_catcher
def load_col_model():
    text = get_resource_text()
    
    tb = TelemetryBuffer.get_instance()
    
    activities = [
        {'index': 'id', 'name': 'id', 'key': True, 'hidden': True, 'sortable': False},
        {
            'label': tb.get_field('dhcp', 'time')['name'],
            'index': 'time', 'name': 'time',
            'width': 190, 'sortable': False
        },
        {
            'label': tb.get_field('dhcp', 'server_id')['name'],
            'index': 'server_id', 'name': 'server_id',
            'width': 100, 'sortable': False
        },
        {
            'label': tb.get_field('dhcp', 'lease_per_second')['name'],
            'index': 'lease_per_second', 'name': 'lease_per_second',
            'width': 90, 'align': 'right', 'sortable': False,
            'formatter':'number',
            'formatoptions': {
                'decimalSeparator': ".",
                'decimalPlaces' : 3
            }
        },
        {
            'label': tb.get_field('dhcp', 'discover_received')['name'],
            'index': 'discover_received', 'name': 'discover_received',
            'width': 90, 'align': 'right', 'sortable': False
        },
        {
            'label': tb.get_field('dhcp', 'request_received')['name'],
            'index': 'request_received', 'name': 'request_received',
            'width': 90, 'align': 'right', 'sortable': False
        },
        {
            'label': tb.get_field('dhcp', 'offer_sent')['name'],
            'index': 'offer_sent', 'name': 'offer_sent',
            'width': 90, 'align': 'right', 'sortable': False
        },
        {
            'label': tb.get_field('dhcp', 'ack_sent')['name'],
            'index': 'ack_sent', 'name': 'ack_sent',
            'width': 90, 'align': 'right', 'sortable': False
        },
    ]
    return jsonify({'title': text['label_statistics_list'], 'columns': activities})

@route(app, '/dhcp_statistics_viewer/load_statistics')
@util.workflow_permission_required('dhcp_statistics_viewer_page')
@util.exception_catcher
def load_statistics():
    tb = TelemetryBuffer.get_instance()
    start = int(request.args.get('start', '0'))
    count = int(request.args.get('count', '100'))
    return jsonify(tb.collect_data('dhcp', start, count))

@route(app, '/dhcp_statistics_viewer/get_statistics/<key>')
@util.workflow_permission_required('dhcp_statistics_viewer_page')
@util.exception_catcher
def get_statistics(key):
    tb = TelemetryBuffer.get_instance()
    return jsonify(tb.get_data('dhcp', key))

@route(app, '/dhcp_statistics_viewer/dhcp_statistics_viewer_endpoint')
@util.workflow_permission_required('dhcp_statistics_viewer_page')
@util.exception_catcher
@util.ui_secure_endpoint
def dhcp_statistics_viewer_dhcp_statistics_viewer_page():
    form = GenericFormTemplate()
    return render_template(
        'dhcp_statistics_viewer_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )


@route(app, '/dhcp_statistics_viewer/form', methods=['POST'])
@util.workflow_permission_required('dhcp_statistics_viewer_page')
@util.exception_catcher
@util.ui_secure_endpoint
def dhcp_statistics_viewer_dhcp_statistics_viewer_page_form():
    form = GenericFormTemplate()
    # Put form processing logic here
    g.user.logger.info('SUCCESS')
    flash('success', 'succeed')
    return redirect(url_for('dhcp_statistics_viewerdhcp_statistics_viewer_dhcp_statistics_viewer_page'))
