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
# By: Akira Goto (agoto@bluecatnetworks.com)
# Date: 2019-10-30
# Gateway Version: 19.8.1
# Description: Juniper Mist Importer page.py

# Various Flask framework items.
import os
import sys
import codecs

from flask import request, url_for, redirect, render_template, flash, g, jsonify
from wtforms.validators import URL, DataRequired
from wtforms import StringField, BooleanField, SubmitField

from bluecat.wtform_extensions import GatewayForm
from bluecat import route, util
import config.default_config as config
from main_app import app

from .mist_importer import MistImporter

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
    workflow_name = 'mist_importer'
    workflow_permission = 'mist_importer_page'

    text=util.get_text(module_path(), config.language)
    require_message=text['require_message']

    org_id = StringField(
        label=text['label_org_id'],
        validators=[DataRequired(message=require_message)]
    )
    api_token = StringField(
        label=text['label_api_token'],
        validators=[DataRequired(message=require_message)]
    )
    site_name = StringField(
        label=text['label_site_name'],
        validators=[DataRequired(message=require_message)]
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
@route(app, '/mist_importer/mist_importer_endpoint')
@util.workflow_permission_required('mist_importer_page')
@util.exception_catcher
def mist_importer_mist_importer_page():
    form = GenericFormTemplate()

    mist_importer = MistImporter.get_instance(debug=True)

    value = mist_importer.get_value('org_id')
    if value is not None:
        form.org_id.data = value
    value = mist_importer.get_value('api_token')
    if value is not None:
        form.api_token.data = value
    value = mist_importer.get_value('site_name')
    if value is not None:
        form.site_name.data = value
    value = mist_importer.get_value('include_matches')
    if value is not None:
        form.include_matches.data = value
    value = mist_importer.get_value('include_ipam_only')
    if value is not None:
        form.include_ipam_only.data = value

    return render_template(
        'mist_importer_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/mist_importer/load_col_model')
@util.workflow_permission_required('mist_importer_page')
@util.exception_catcher
def load_col_model():
    text=util.get_text(module_path(), config.language)

    clients = [
        {'index':'id', 'name':'id', 'hidden':True, 'sortable':False},
        {'index':'network_id', 'name':'network_id', 'hidden':True, 'sortable':False},
        {'index':'order', 'name':'order', 'hidden':True, 'sortable':False},
        {'index':'name', 'name':'name', 'hidden':True, 'sortable':False},
        {'index':'system', 'name':'system', 'hidden':True, 'sortable':False},
        {'index':'detail_link', 'name':'detail_link', 'hidden':True, 'sortable':False},
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
            'width':200, 'sortable':False
        },
        {
            'label': text['label_col_state'], 'index':'state', 'name':'state',
            'width':50, 'align':'center', 'sortable':False,
            'formatter': 'select',
            'formatoptions': {
                'value': {
                    'UNKNOWN': '<img src="img/help.gif" title="Unknown" width="16" height="16">',
                    'MATCH': '<img src="img/check.gif" title="Match" width="16" height="16">',
                    'MISMATCH': '<img src="img/about.gif" title="Mismatch" width="16" height="16">',
                    'RECLAIM': '<img src="img/data_delete.gif" title="Reclam" width="16" height="16">'
                }
            }
        },
        {
            'label': text['label_col_lastfound'], 'index':'last_found', 'name':'last_found',
            'width':140, 'align':'center', 'sortable':False
        }
    ]
    return jsonify(clients)

@route(app, '/mist_importer/get_clients')
@util.workflow_permission_required('mist_importer_page')
@util.exception_catcher
def get_clients():
    clients = []
    configuration = get_configuration()
    if configuration is not None:
        mist_importer = MistImporter.get_instance()
        mist_importer.collect_clients(configuration)
        clients = mist_importer.get_clients()
    return jsonify(clients)

@route(app, '/mist_importer/load_clients')
@util.workflow_permission_required('mist_importer_page')
@util.exception_catcher
def load_clients():
    mist_importer = MistImporter.get_instance()
    clients = mist_importer.get_clients()
    return jsonify(clients)

@route(app, '/mist_importer/update_config', methods=['POST'])
@util.workflow_permission_required('mist_importer_page')
@util.exception_catcher
def update_config():
    config = request.get_json()
    mist_importer = MistImporter.get_instance()
    mist_importer.set_value('org_id', config['org_id'])
    mist_importer.set_value('api_token', config['api_token'])
    mist_importer.set_value('site_name', config['site_name'])
    mist_importer.set_value('include_matches', config['include_matches'])
    mist_importer.set_value('include_ipam_only', config['include_ipam_only'])
    mist_importer.save()
    return jsonify(success=True)

@route(app, '/mist_importer/push_selected_clients', methods=['POST'])
@util.workflow_permission_required('mist_importer_page')
@util.exception_catcher
def push_selected_clients():
    new_clients = []
    client_ids = request.get_json()
    mist_importer = MistImporter.get_instance()

    for client in mist_importer.get_clients():
        if client['id'] in client_ids:
            new_clients.append(client)

    mist_importer.set_clients(new_clients)
    return jsonify(success=True)

@route(app, '/mist_importer/clear_clients', methods=['POST'])
@util.workflow_permission_required('mist_importer_page')
@util.exception_catcher
def clear_clients():
    mist_importer = MistImporter.get_instance()
    mist_importer.clear_clients()
    return jsonify(success=True)

@route(app, '/mist_importer/form', methods=['POST'])
@util.workflow_permission_required('mist_importer_page')
@util.exception_catcher
def mist_importer_mist_importer_page_form():
    form = GenericFormTemplate()
    text=util.get_text(module_path(), config.language)
    if form.validate_on_submit():
        mist_importer = MistImporter.get_instance()
        mist_importer.set_value('org_id', form.org_id.data)
        mist_importer.set_value('api_token', form.api_token.data)
        mist_importer.set_value('site_name', form.site_name.data)
        mist_importer.set_value('include_matches', form.include_matches.data)
        mist_importer.set_value('include_ipam_only', form.include_ipam_only.data)
        mist_importer.save()

        configuration = get_configuration()
        mist_importer.import_clients(configuration)
        mist_importer.collect_clients(configuration)

        # Put form processing code here
        g.user.logger.info('SUCCESS')
        flash(text['imported_message'], 'succeed')
        return redirect(url_for('mist_importermist_importer_mist_importer_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'mist_importer_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
