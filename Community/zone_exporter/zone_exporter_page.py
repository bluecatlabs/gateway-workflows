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
# Description: Zone Exporter Page

# Various Flask framework items.
import datetime
import os
import sys

from flask import url_for, redirect, render_template, flash, g, jsonify, send_file
from wtforms import SelectField

from bluecat import route, util
from bluecat.wtform_extensions import GatewayForm

import config.default_config as config
from main_app import app

from .exporter import module_path, get_resource_text
from .exporter import load_config, construct_node
from .exporter import export_as_csv, export_as_excel

CSV_MIMETYPE = 'text/csv'
XLSX_MIMETYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
CSV_FILE_NAME = 'exported{0:%Y%m%d%H%M%S}.csv'
XLSX_FILE_NAME = 'exported{0:%Y%m%d%H%M%S}.xlsx'

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
    workflow_name = 'zone_exporter'
    workflow_permission = 'zone_exporter_page'
    
    text=get_resource_text()
    
    format = SelectField(
        label=text['label_format'],
        choices= [('excel','Excel'), ('csv','CSV')]
    )
    contents = SelectField(
        label=text['label_contents'],
        choices= [
            ('struct', text['title_structure']),
            ('records', text['title_records']),
            ('both', text['title_both'])
        ]
    )
    

# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/zone_exporter/zone_exporter_endpoint')
@util.workflow_permission_required('zone_exporter_page')
@util.exception_catcher
def zone_exporter_zone_exporter_page():
    form = GenericFormTemplate()
    return render_template(
        'zone_exporter_page.html',
        form=form,
        text=get_resource_text(),
        options=g.user.get_options(),
    )

@route(app, '/zone_exporter/form', methods=['POST'])
@util.workflow_permission_required('zone_exporter_page')
@util.exception_catcher
def zone_exporter_zone_exporter_page_form():
    form = GenericFormTemplate()
    if form.validate_on_submit():
        # Put form processing code here
        g.user.logger.info('SUCCESS')
        flash('success', 'succeed')
        return redirect(url_for('zone_exporterzone_exporter_zone_exporter_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'zone_exporter_page.html',
            form=form,
            text=get_resource_text(),
            options=g.user.get_options(),
        )

@route(app, '/zone_exporter/load_col_model')
@util.workflow_permission_required('zone_exporter_page')
@util.exception_catcher
def load_col_model():
    nodes = []
    load_config(module_path(), nodes)
    return jsonify(nodes)

@route(app, '/zone_exporter/load_initial_data')
@util.workflow_permission_required('zone_exporter_page')
@util.exception_catcher
def load_initial_data():
    nodes = []
    configuration = get_configuration()
    if configuration is not None:
        views = configuration.get_views()
        for view in views:
            nodes.append(construct_node(None, 0, view))
        nodes.sort(key = lambda node: node['name'])

    return jsonify(nodes)

@route(app, '/zone_exporter/load_children_data/<int:id>/<int:level>')
@util.workflow_permission_required('zone_exporter_page')
@util.exception_catcher
def load_children_data(id, level):
    nodes = []
    parent = g.user.get_api().get_entity_by_id(id)
    if parent is not None:
        zones = parent.get_children_of_type('Zone')
        for zone in zones:
            nodes.append(construct_node(id, level, zone))
        nodes.sort(key = lambda node: node['name'])
        
    return jsonify(nodes)

@route(app, '/zone_exporter/load_file/<int:id>/<format>/<contents>')
@util.workflow_permission_required('zone_exporter_page')
@util.exception_catcher
def load_file(id, format, contents):
    now = datetime.datetime.now()
    dirname = module_path()
    
    if id == 0:
        configuration = get_configuration()
        id = configuration.get_id()
    if format == 'csv':
        filename = CSV_FILE_NAME.format(now)
        mimetype = CSV_MIMETYPE
        export_as_csv(g.user.get_api(), dirname, filename, id, contents)
    else:
        filename = XLSX_FILE_NAME.format(now)
        mimetype = XLSX_MIMETYPE
        export_as_excel(g.user.get_api(), dirname, filename, id, contents)
        
    return send_file(dirname + '/' + filename,
                         mimetype=mimetype,
                         attachment_filename=filename,
                         as_attachment=True) 