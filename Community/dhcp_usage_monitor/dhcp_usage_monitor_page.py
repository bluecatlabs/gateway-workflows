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
# Date: 2022-07-10
# Gateway Version: 22.4.1
# Description: DHCP Usage Monitor 

import os
import sys
import codecs

from flask import url_for, redirect, render_template, flash, g, jsonify, request
from wtforms import StringField, PasswordField, SelectField, SubmitField, FileField
from wtforms.fields import IntegerField

from bluecat.wtform_extensions import GatewayForm
from bluecat import route, util
import config.default_config as config
from main_app import app

from .dhcp_usage_monitor import DUMonitor

def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))

def get_configuration(api, config_name):
    configuration = api.get_configuration(config_name)
    return configuration


class GenericFormTemplate(GatewayForm):
    workflow_name = 'dhcp_usage_monitor'
    workflow_permission = 'dhcp_usage_monitor_page'
    
    text=util.get_text(module_path(), config.language)
    separator = text['separator']
    
    # Top Pane
    range = StringField(
        label=text['label_col_range'] + separator
    )
    low_watermark = IntegerField(
        label=text['label_col_low_watermark'] + separator,
        default=0,
        render_kw={'style': 'text-align: right;', 'min': '0', 'max': '100'}
    )
    high_watermark = IntegerField(
        label=text['label_col_high_watermark'] + separator,
        default=100,
        render_kw={'style': 'text-align: right;', 'min': '0', 'max': '100'}
    )
    upload_file = FileField(
        label=text['label_upload_file'] + separator
    )
    
    # Trap Pan
    ipaddress = StringField(
        label=text['label_col_ipaddress'] + separator
    )
    port = IntegerField(
        label=text['label_col_port'] + separator,
        default=162,
        render_kw={'style': 'text-align: right;', 'min': '1'}
    )
    snmpver = SelectField(
        label=text['label_col_snmpver'] + separator,
        choices=[('v1', 'v1'), ('v2c', 'v2c')],
        render_kw={'style': 'text-align: center;'}
    )
    comstr = StringField(
        label=text['label_col_comstr'] + separator
    )
    
    # BAM Pan
    bam_ip = StringField(
        label=text['label_bam_ip']
    )
    bam_user = StringField(
        label=text['label_bam_user']
    )
    bam_pass = PasswordField(
        label=text['label_bam_pass']
    )
    interval = IntegerField(
        label=text['label_interval'],
        default=360,
        render_kw={'style': 'text-align: right;', 'min': '0'}
    )
    
    submit = SubmitField(label=text['label_submit'])


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/dhcp_usage_monitor/load_col_model')
@util.workflow_permission_required('dhcp_usage_monitor_page')
@util.exception_catcher
def load_col_model():
    text=util.get_text(module_path(), config.language)
    t_unknown = text['label_st_unknown']
    t_normal = text['label_st_normal']
    t_lower = text['label_st_lower']
    t_higher = text['label_st_higher']

    nodes = {
        'du_nodes': [
            {'index':'id', 'name':'id', 'hidden':True, 'key': True, 'sortable':False},
            {
                'label': text['label_col_range'], 'index':'range', 'name':'range',
                'width':220, 'sortable':True
            },
            {
                'label': text['label_col_low_watermark'], 'index':'low_watermark', 'name':'low_watermark',
                'width':100, 'align':'right', 'sortable':False
            },
            {
                'label': text['label_col_high_watermark'], 'index':'high_watermark', 'name':'high_watermark',
                'width':100, 'align':'right', 'sortable':False
            },
            {
                'label': text['label_col_status'], 'index':'status', 'name':'status',
                'width':60, 'align':'center', 'sortable':False,
                'formatter': 'select',
                'formatoptions': {
                    'value': {
                        'UNKNOWN': '<img src="img/unknown.gif" title="%s" width="16" height="16">' % t_unknown,
                        'NORMAL': '<img src="img/good.gif" title="%s" width="16" height="16">' % t_normal,
                        'LOWER': '<img src="img/warning.gif" title="%s" width="16" height="16">' % t_lower,
                        'HIGHER': '<img src="img/bad.gif" title="%s" width="16" height="16">' % t_higher
                    }
                }
            },
            {
                'label': text['label_col_usage'], 'index':'usage', 'name':'usage',
                'width':90, 'align':'right', 'sortable':True, 'sorttype': 'float',
                'formatter': 'number',
                'formatoptions': {
                    'decimalSeparator': '.', 'decimalPlaces': 2
                }
            },
            {
                'label': text['label_col_dhcp_count'], 'index':'dhcp_count', 'name':'dhcp_count',
                'width':100, 'align':'right', 'sortable':True, 'sorttype': 'int'
            },
            {
                'label': text['label_col_leased_count'], 'index':'leased_count', 'name':'leased_count',
                'width':100, 'align':'right', 'sortable':True, 'sorttype': 'int'
            }
        ],
        'tp_nodes': [
            {
                'label': text['label_col_ipaddress'], 'index':'ipaddress', 'name':'ipaddress',
                'key': True, 'width':140, 'sortable':False
            },
            {
                'label': text['label_col_port'], 'index':'port', 'name':'port',
                'width':60, 'align':'right', 'sortable':False
            },
            {
                'label': text['label_col_snmpver'], 'index':'snmpver', 'name':'snmpver',
                'width':80, 'align':'center', 'sortable':False
            },
            {
                'label': text['label_col_comstr'], 'index':'comstr', 'name':'comstr',
                'width':300, 'sortable':False
            }
        ]
    }
    return jsonify(nodes)
    

@route(app, '/dhcp_usage_monitor/get_network_suggestions', methods=['POST'])
@util.workflow_permission_required('dhcp_usage_monitor_page')
@util.exception_catcher
def get_network_suggestions():
    cidr = request.get_json()
    du_monitor = DUMonitor.get_instance()
    
    api = g.user.get_api()
    configuration = api.get_configuration(config.default_configuration)
    suggestions = du_monitor.get_network_suggestions(api.spec_api, configuration.get_id(), cidr)
    return jsonify(suggestions)

@route(app, '/dhcp_usage_monitor/get_network_id')
@util.workflow_permission_required('dhcp_usage_monitor_page')
@util.exception_catcher
def get_network_id():
    du_monitor = DUMonitor.get_instance()
    
    args = request.args
    range = args.get('range')
    
    api = g.user.get_api()
    configuration = api.get_configuration(config.default_configuration)
    network_id = du_monitor.get_network_id(api.spec_api, configuration.get_id(), range)
    return jsonify(network_id)

@route(app, '/dhcp_usage_monitor/get_dhcp_usage')
@util.workflow_permission_required('dhcp_usage_monitor_page')
@util.exception_catcher
def get_dhcp_usage():
    du_monitor = DUMonitor.get_instance()
    
    args = request.args
    range = args.get('range')
    low_watermark = int(args.get('low_watermark'))
    high_watermark = int(args.get('high_watermark'))
    
    api = g.user.get_api()
    configuration = api.get_configuration(config.default_configuration)
    network_id = du_monitor.get_network_id(api.spec_api, configuration.get_id(), range)
    
    dhcp_usage = \
        du_monitor.get_dhcp_usage(api.spec_api, network_id, range, low_watermark, high_watermark)
    return jsonify(dhcp_usage)

@route(app, '/dhcp_usage_monitor/get_dhcp_usages')
@util.workflow_permission_required('dhcp_usage_monitor_page')
@util.exception_catcher
def get_dhcp_usages():
    du_monitor = DUMonitor.get_instance()
    du_monitor.collect_dhcp_usages()
    dhcp_usages = du_monitor.get_dhcp_usages()
    return jsonify(dhcp_usages)


@route(app, '/dhcp_usage_monitor/load_dhcp_usages')
@util.workflow_permission_required('dhcp_usage_monitor_page')
@util.exception_catcher
def load_dhcp_usages():
    du_monitor = DUMonitor.get_instance()
    dhcp_usages = du_monitor.get_dhcp_usages()
    return jsonify(dhcp_usages)

@route(app, '/dhcp_usage_monitor/update_dhcp_usages', methods=['POST'])
@util.workflow_permission_required('dhcp_usage_monitor_page')
@util.exception_catcher
def update_dhcp_usages():
    dhcp_usages = request.get_json()
    du_monitor = DUMonitor.get_instance()
    
    for dhcp_usage in dhcp_usages:
        dhcp_usage['id'] = int(dhcp_usage['id'])
        dhcp_usage['low_watermark'] = int(dhcp_usage['low_watermark'])
        dhcp_usage['high_watermark'] = int(dhcp_usage['high_watermark'])
        dhcp_usage['usage'] = float(dhcp_usage['usage'])
        dhcp_usage['dhcp_count'] = int(dhcp_usage['dhcp_count'])
        dhcp_usage['leased_count'] = int(dhcp_usage['leased_count'])
        
        # The following should not necessary if we can get unformatted data
        if dhcp_usage['status'] == '':
            dhcp_usage['status'] = du_monitor.get_status(dhcp_usage)
            
    du_monitor.set_dhcp_usages(dhcp_usages)
    return jsonify(success=True)

@route(app, '/dhcp_usage_monitor/load_trap_servers')
@util.workflow_permission_required('dhcp_usage_monitor_page')
@util.exception_catcher
def load_trap_servers():
    du_monitor = DUMonitor.get_instance()
    trap_servers = du_monitor.get_value('trap_servers')
    return jsonify(trap_servers)

@route(app, '/dhcp_usage_monitor/update_trap_servers', methods=['POST'])
@util.workflow_permission_required('dhcp_usage_monitor_page')
@util.exception_catcher
def update_trap_servers():
    trap_servers = request.get_json()
    du_monitor = DUMonitor.get_instance()
    
    for trap_server in trap_servers:
        trap_server['port'] = int(trap_server['port'])
    du_monitor.set_trap_servers(trap_servers)
    return jsonify(success=True)

@route(app, '/dhcp_usage_monitor/dhcp_usage_monitor_endpoint')
@util.workflow_permission_required('dhcp_usage_monitor_page')
@util.exception_catcher
@util.ui_secure_endpoint
def dhcp_usage_monitor_dhcp_usage_monitor_page():
    form = GenericFormTemplate()
    du_monitor = DUMonitor.get_instance()
    
    form.bam_ip.data = du_monitor.get_value('bam_ip')
    form.bam_user.data = du_monitor.get_value('bam_user')
    form.interval.data = du_monitor.get_value('execution_interval')
    
    return render_template(
        'dhcp_usage_monitor_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )


@route(app, '/dhcp_usage_monitor/form', methods=['POST'])
@util.workflow_permission_required('dhcp_usage_monitor_page')
@util.exception_catcher
@util.ui_secure_endpoint
def dhcp_usage_monitor_dhcp_usage_monitor_page_form():
    form = GenericFormTemplate()
    text=util.get_text(module_path(), config.language)
    du_monitor = DUMonitor.get_instance()
    
    if form.bam_ip.data != du_monitor.get_value('bam_ip'):
        du_monitor.set_value('bam_ip', form.bam_ip.data)
    if form.bam_user.data != du_monitor.get_value('bam_user'):
        du_monitor.set_value('bam_user', form.bam_user.data)
    if form.bam_pass.data != '':
        du_monitor.set_value('bam_pass', form.bam_pass.data)
    if form.interval.data != du_monitor.get_value('execution_interval'):
        du_monitor.set_value('execution_interval', form.interval.data)
        du_monitor.register_job()
        
    du_monitor.save()
    g.user.logger.info('SUCCESS')
    flash(text['saved_message'], 'succeed')
    return redirect(url_for('dhcp_usage_monitordhcp_usage_monitor_dhcp_usage_monitor_page'))
