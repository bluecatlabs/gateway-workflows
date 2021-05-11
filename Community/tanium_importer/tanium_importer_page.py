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
# By: Akira Goto (agoto@bluecatnetworks.com)
# Date: 2020-05-31
# Gateway Version: 20.12.1
# Description: Tanium Importer page.py

import os
import sys
import codecs

from flask import request, url_for, redirect, render_template, flash, g, jsonify
from wtforms.validators import URL, DataRequired
from wtforms import StringField, PasswordField, IntegerField, BooleanField, SubmitField

from bluecat.wtform_extensions import GatewayForm
from bluecat import route, util
import config.default_config as config
from main_app import app

from .tanium_importer import TaniumImporter

def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))

def get_configuration():
    configuration = None
    if g.user:
        configuration = g.user.get_api().get_configuration(config.default_configuration)
    return configuration
    

class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'tanium_importer'
    workflow_permission = 'tanium_importer_page'
    
    text=util.get_text(module_path(), config.language)
    require_message=text['require_message']
    
    server_addr = StringField(
        label=text['label_server_addr'],
        validators=[DataRequired(message=require_message)],
        render_kw={"placeholder": "ex. 10.10.10.10 or taniumserver.domain.local (FQDN)"}
    )
    user_id = StringField(
        label=text['label_user_id'],
        validators=[DataRequired(message=require_message)]
    )
    password = PasswordField(
        label=text['label_password']
    )
    target_networks = StringField(
        label=text['label_target_networks'],
        validators=[DataRequired(message=require_message)],
        render_kw={"placeholder": "ex. 10.0.0.0/24, 10.10.10.0/24"}
    )
    style={'style': 'text-align: right;'}
    retry_count = IntegerField(
        label=text['label_retry_count'],
        validators=[DataRequired(message=require_message)],
        render_kw=style
    )
    interval = IntegerField(
        label=text['label_interval'],
        validators=[DataRequired(message=require_message)],
        render_kw=style
    )
    include_discovery = BooleanField(
        label='',
        default='checked'
    )
        
    include_matches = BooleanField(
        label='',
        default='checked'
    )
    
    include_ipam_only = BooleanField(
        label='',
        default='checked'
    )
    
    submit = SubmitField(label=text['label_submit'])

# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/tanium_importer/tanium_importer_endpoint')
@util.workflow_permission_required('tanium_importer_page')
@util.exception_catcher
def tanium_importer_tanium_importer_page():
    form = GenericFormTemplate()
    
    tanium_importer = TaniumImporter.get_instance(debug=True)
    
    value = tanium_importer.get_value('server_addr')
    if value is not None:
        form.server_addr.data = value
    value = tanium_importer.get_value('user_id')
    if value is not None:
        form.user_id.data = value
    value = tanium_importer.get_value('password')
    if value is not None:
        form.password.data = value
    value = tanium_importer.get_value('target_networks')
    if value is not None:
        form.target_networks.data = value
    value = tanium_importer.get_value('retry_count')
    if value is not None:
        form.retry_count.data = value
    value = tanium_importer.get_value('interval')
    if value is not None:
        form.interval.data = value
    value = tanium_importer.get_value('include_discovery')
    if value is not None:
        form.include_discovery.data = value
    value = tanium_importer.get_value('include_matches')
    if value is not None:
        form.include_matches.data = value
    value = tanium_importer.get_value('include_ipam_only')
    if value is not None:
        form.include_ipam_only.data = value
    
    return render_template(
        'tanium_importer_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/tanium_importer/load_col_model')
@util.workflow_permission_required('tanium_importer_page')
@util.exception_catcher
def load_col_model():
    text=util.get_text(module_path(), config.language)
    
    links = '<img src="{icon}" title="{title}" width="16" height="16">'
    value_table = {
        'UNKNOWN': links.format(icon='img/help.gif', title=text['label_state_unknown']),
        'MATCH': links.format(icon='img/check.gif', title=text['label_state_match']),
        'MISMATCH': links.format(icon='img/about.gif', title=text['label_state_mismatch']),
        'RECLAIM': links.format(icon='img/data_delete.gif', title=text['label_state_reclaim'])
    }

    col_model = [
        {'index':'id', 'name':'id', 'hidden':True, 'sortable':False},
        {'index':'order', 'name':'order', 'hidden':True, 'sortable':False},
        {'index':'name', 'name':'name', 'hidden':True, 'sortable':False},
        {'index':'system', 'name':'system', 'hidden':True, 'sortable':False},
        {'index':'detail_link', 'name':'detail_link', 'hidden':True, 'sortable':False},
        {
            'label': text['label_col_managed'], 'index':'managed', 'name':'managed',
            'width':40, 'align':'center', 'sortable':False,
            'formatter': 'select',
            'formatoptions': {
                'value': {
                    'UNKNOWN': '<img src="img/unknown.gif" title="Unknown" width="16" height="16">',
                    'MANAGED': '<img src="img/good.gif" title="Tanium Installed" width="16" height="16">'
                }
            }
        },
        {
            'label': text['label_col_ipaddr'], 'index':'ipaddr', 'name':'ipaddr',
            'width':100, 'align':'center', 'sortable':False
        },
        {
            'label': text['label_col_macaddr'], 'index':'macaddr', 'name':'macaddr',
            'width':130, 'align':'center', 'sortable':False
        },
        {
            'label': text['label_col_name'], 'index':'linked_name', 'name':'linked_name',
            'width':140, 'sortable':False
        },
        {
            'label': text['label_col_system'], 'index':'system', 'name':'system',
            'width':240, 'sortable':False
        },
        {
            'label': text['label_col_state'], 'index':'state', 'name':'state',
            'width':50, 'align':'center', 'sortable':False,
            'formatter': 'select',
            'formatoptions': {
                'value': value_table
            }
        },
        {
            'label': text['label_col_lastfound'], 'index':'last_found', 'name':'last_found',
            'width':140, 'align':'center', 'sortable':False,
            'formatter': 'date',
            'formatoptions': {
                'srcformat': 'ISO8601Long',
                'newformat': 'Y-m-d H:i:s',
                'userLocalTime': True
            }
        }
    ]
    return jsonify({'title': text['label_client_list'], 'columns': col_model})

@route(app, '/tanium_importer/get_clients')
@util.workflow_permission_required('tanium_importer_page')
@util.exception_catcher
def get_clients():
    clients = []
    configuration = get_configuration()
    if configuration is not None:
        tanium_importer = TaniumImporter.get_instance()
        tanium_importer.collect_clients(configuration)
        clients = tanium_importer.get_clients()
    return jsonify(clients)

@route(app, '/tanium_importer/load_clients')
@util.workflow_permission_required('tanium_importer_page')
@util.exception_catcher
def load_clients():
    tanium_importer = TaniumImporter.get_instance()
    clients = tanium_importer.get_clients()
    return jsonify(clients)

@route(app, '/tanium_importer/update_config', methods=['POST'])
@util.workflow_permission_required('tanium_importer_page')
@util.exception_catcher
def update_config():
    config = request.get_json()
    tanium_importer = TaniumImporter.get_instance()
    tanium_importer.set_value('server_addr', config['server_addr'])
    tanium_importer.set_value('user_id', config['user_id'])
    if config['password'] != '':
        tanium_importer.set_value('password', config['password'])
    tanium_importer.set_value('target_networks', config['target_networks'])
    value = config['retry_count'] if config['retry_count'] is not None else 0
    tanium_importer.set_value('retry_count', value)
    value = config['interval'] if config['interval'] is not None else 0
    tanium_importer.set_value('interval', value)
    tanium_importer.set_value('include_discovery', config['include_discovery'])
    tanium_importer.set_value('include_matches', config['include_matches'])
    tanium_importer.set_value('include_ipam_only', config['include_ipam_only'])
    tanium_importer.save()
    return jsonify(success=True)

@route(app, '/tanium_importer/push_selected_clients', methods=['POST'])
@util.workflow_permission_required('tanium_importer_page')
@util.exception_catcher
def push_selected_clients():
    new_clients = []
    client_ids = request.get_json()
    tanium_importer = TaniumImporter.get_instance()
    
    for client in tanium_importer.get_clients():
        if client['id'] in client_ids:
            new_clients.append(client)
            
    tanium_importer.set_clients(new_clients)
    return jsonify(success=True)

@route(app, '/tanium_importer/clear_clients', methods=['POST'])
@util.workflow_permission_required('tanium_importer_page')
@util.exception_catcher
def clear_clients():
    tanium_importer = TaniumImporter.get_instance()
    tanium_importer.clear_clients()
    return jsonify(success=True)

@route(app, '/tanium_importer/form', methods=['POST'])
@util.workflow_permission_required('tanium_importer_page')
@util.exception_catcher
def tanium_importer_tanium_importer_page_form():
    form = GenericFormTemplate()
    text=util.get_text(module_path(), config.language)
    if form.validate_on_submit():
        tanium_importer = TaniumImporter.get_instance()
        tanium_importer.set_value('server_addr', form.server_addr.data)
        tanium_importer.set_value('user_id', form.user_id.data)
        if form.password.data != '':
            tanium_importer.set_value('password', form.password.data)
        tanium_importer.set_value('target_networks', form.target_networks.data)
        value = form.retry_count.data if form.retry_count.data is not None else 0
        tanium_importer.set_value('retry_count', value)
        value = form.interval.data if form.interval.data is not None else 0
        tanium_importer.set_value('interval', value)
        tanium_importer.set_value('include_discovery', form.include_discovery.data)
        tanium_importer.set_value('include_matches', form.include_matches.data)
        tanium_importer.set_value('include_ipam_only', form.include_ipam_only.data)
        tanium_importer.save()
        
        configuration = get_configuration()
        tanium_importer.import_clients(configuration)
        tanium_importer.collect_clients(configuration)
        
        # Put form processing code here
        g.user.logger.info('SUCCESS')
        flash(text['imported_message'], 'succeed')
        return redirect(url_for('tanium_importertanium_importer_tanium_importer_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'tanium_importer_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )

