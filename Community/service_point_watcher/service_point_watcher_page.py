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
# Date: 2019-08-28
# Gateway Version: 19.5.1
# Description: Service Point Watcher page.py

# Various Flask framework items.
import os
import sys
import codecs

from flask import request, url_for, redirect, render_template, flash, g, jsonify
from wtforms.validators import URL, DataRequired
from wtforms import StringField, FileField, SubmitField

from bluecat.wtform_extensions import GatewayForm
from bluecat import route, util
import config.default_config as config
from main_app import app

from .sp_watcher import SPWatcher


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))

class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'service_point_watcher'
    workflow_permission = 'service_point_watcher_page'

    text=util.get_text(module_path(), config.language)
    invalid_url_message=text['invalid_url_message']
    require_message=text['require_message']

    # DNS Edge Pane
    edge_url = StringField(
        label=text['label_config_url'],
        validators=[URL(message=invalid_url_message)],
        render_kw={"placeholder": "https://api-<Edge Instance>.bluec.at"}
    )
    edge_key_file = FileField(
        text['label_config_key_file']
    )
    edge_client_id = StringField(
        label=text['label_config_client_id'],
        validators=[DataRequired(message=require_message)]
    )
    edge_secret = StringField(
        label=text['label_config_secret'],
        validators=[DataRequired(message=require_message)]
    )
    execution_interval = StringField(
        label=text['label_config_interval'],
        validators=[DataRequired(message=require_message)]
    )
    timeout = StringField(
        label=text['label_config_timeout'],
        validators=[DataRequired(message=require_message)]
    )

    submit = SubmitField(label=text['label_submit'])



# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/service_point_watcher/service_point_watcher_endpoint')
@util.workflow_permission_required('service_point_watcher_page')
@util.exception_catcher
def service_point_watcher_service_point_watcher_page():
    form = GenericFormTemplate()
    sp_watcher = SPWatcher.get_instance()

    value = sp_watcher.get_value('edge_url')
    if value is not None:
        form.edge_url.data = value
    value = sp_watcher.get_value('edge_client_id')
    if value is not None:
        form.edge_client_id.data = value
    value = sp_watcher.get_value('edge_secret')
    if value is not None:
        form.edge_secret.data = value
    value = sp_watcher.get_value('execution_interval')
    if value is not None:
        form.execution_interval.data = str(value)
    value = sp_watcher.get_value('timeout')
    if value is not None:
        form.timeout.data = str(value)

    return render_template(
        'service_point_watcher_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )


@route(app, '/service_point_watcher/load_col_model')
@util.workflow_permission_required('service_point_watcher_page')
@util.exception_catcher
def load_col_model():
    text=util.get_text(module_path(), config.language)

    nodes = {
        'sp_nodes': [
            {'index':'id', 'name':'id', 'hidden':True, 'sortable':False},
            {
                'label': text['label_col_watch'], 'index':'watch', 'name':'watch',
                'width':60, 'align':'center', 'sortable':False,
                'editoptions': { 'value':'True:False'},'formatter':'checkbox'
            },
            {
                'label': text['label_col_name'], 'index':'name', 'name':'name',
                'width':220, 'sortable':False
            },
            {
                'label': text['label_col_ipaddress'], 'index':'ipaddress', 'name':'ipaddress',
                'width':100, 'align':'center', 'sortable':False
            },
            {
                'label': text['label_col_site'], 'index':'site', 'name':'site',
                'width':180, 'sortable':False
            },
            {
                'label': text['label_col_connected'], 'index':'connected', 'name':'connected',
                'width':80, 'align':'center', 'sortable':False,
                'formatter': 'select',
                'formatoptions': {
                    'value': {
                        'CONNECTED': '<img src="img/check.gif" title="Connected" width="16" height="16">',
                        'DISCONNECTED': '<img src="img/help.gif" title="Disconnected" width="16" height="16">'
                    }
                }
            },
            {
                'label': text['label_col_status'], 'index':'status', 'name':'status',
                'width':60, 'align':'center', 'sortable':False,
                'formatter': 'select',
                'formatoptions': {
                    'value': {
                        'UNKNOWN': '<img src="img/unknown.gif" title="Unknown" width="16" height="16">',
                        'UNREACHED': '<img src="img/unreached.gif" title="Unreached" width="16" height="16">',
                        'GOOD': '<img src="img/good.gif" title="God" width="16" height="16">',
                        'BAD': '<img src="img/bad.gif" title="Bad" width="16" height="16">'
                    }
                }
            },
            {
                'label': text['label_col_pulling_severity'], 'index':'pulling_severity', 'name':'pulling_severity',
                'width':60, 'align':'center', 'sortable':False,
                'formatter': 'select',
                'formatoptions': {
                    'value': {
                        'UNKNOWN': '<img src="img/unknown.gif" title="Unknown" width="16" height="16">',
                        'NORMAL': '<img src="img/good.gif" title="Normal" width="16" height="16">',
                        'WARNING': '<img src="img/worning.gif" title="Warning" width="16" height="16">',
                        'CRITICAL': '<img src="img/bad.gif" title="Critical" width="16" height="16">'
                    }
                }
            }
        ],
        'tp_nodes': [
            {
                'label': text['label_col_ipaddress'], 'index':'ipaddress', 'name':'ipaddress',
                'width':140, 'sortable':False
            },
            {
                'label': text['label_col_port'], 'index':'port', 'name':'port',
                'width':60, 'sortable':False
            },
            {
                'label': text['label_col_snmpver'], 'index':'snmpver', 'name':'snmpver',
                'width':80, 'sortable':False
            },
            {
                'label': text['label_col_comstr'], 'index':'comstr', 'name':'comstr',
                'width':280, 'sortable':False
            }
        ]
    }
    return jsonify(nodes)

@route(app, '/service_point_watcher/get_service_points')
@util.workflow_permission_required('service_point_watcher_page')
@util.exception_catcher
def get_service_points():
    sp_watcher = SPWatcher.get_instance()
    sp_watcher.collect_service_points()
    service_points = sp_watcher.get_service_point_summaries()
    return jsonify(service_points)

@route(app, '/service_point_watcher/load_service_points')
@util.workflow_permission_required('service_point_watcher_page')
@util.exception_catcher
def load_service_points():
    sp_watcher = SPWatcher.get_instance()
    service_points = sp_watcher.get_service_point_summaries()
    return jsonify(service_points)

@route(app, '/service_point_watcher/update_service_points', methods=['POST'])
@util.workflow_permission_required('service_point_watcher_page')
@util.exception_catcher
def update_service_points():
    service_points = request.get_json()
    sp_watcher = SPWatcher.get_instance()
    sp_watcher.update_service_points(service_points)
    return jsonify(success=True)

@route(app, '/service_point_watcher/load_trap_servers')
@util.workflow_permission_required('service_point_watcher_page')
@util.exception_catcher
def load_trap_servers():
    sp_watcher = SPWatcher.get_instance()
    trap_servers = sp_watcher.get_value('trap_servers')
    return jsonify(trap_servers)

@route(app, '/service_point_watcher/submit_trap_servers', methods=['POST'])
@util.workflow_permission_required('service_point_watcher_page')
@util.exception_catcher
def submit_trap_servers():
    trap_servers = request.get_json()
    sp_watcher = SPWatcher.get_instance()
    sp_watcher.set_value('trap_servers', trap_servers)
    return jsonify(success=True)

@route(app, '/service_point_watcher/form', methods=['POST'])
@util.workflow_permission_required('service_point_watcher_page')
@util.exception_catcher
def service_point_watcher_service_point_watcher_page_form():
    form = GenericFormTemplate()
    sp_watcher = SPWatcher.get_instance()
    text=util.get_text(module_path(), config.language)

    if form.validate_on_submit():
        sp_watcher.set_value('edge_url', form.edge_url.data)
        sp_watcher.set_value('edge_client_id', form.edge_client_id.data)
        sp_watcher.set_value('edge_secret', form.edge_secret.data)
        sp_watcher.set_value('execution_interval', int(form.execution_interval.data))
        sp_watcher.set_value('timeout', int(form.timeout.data))

        sp_watcher.save()
        g.user.logger.info('SAVED')
        flash(text['saved_message'], 'succeed')
        sp_watcher.register_job()
        return redirect(url_for('service_point_watcherservice_point_watcher_service_point_watcher_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'service_point_watcher_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
