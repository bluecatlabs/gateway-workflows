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
# Description: Flip Main-DR Servers Page

# Various Flask framework items.
import os
import sys

from flask import url_for, redirect, render_template, flash, g, jsonify

from bluecat import route, util, entity
import config.default_config as config
from main_app import app

from .flip_normal_dr_form import get_resource_text
from .flip_normal_dr_form import GenericFormTemplate


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/flip_normal_dr/flip_normal_dr_endpoint')
@util.workflow_permission_required('flip_normal_dr_page')
@util.exception_catcher
def flip_normal_dr_flip_normal_dr_page():
    form = GenericFormTemplate()
    return render_template(
        'flip_normal_dr_page.html',
        form=form,
        text=get_resource_text(),
        options=g.user.get_options(),
    )

@route(app, '/flip_normal_dr/form', methods=['POST'])
@util.workflow_permission_required('flip_normal_dr_page')
@util.exception_catcher
def flip_normal_dr_flip_normal_dr_page_form():
    form = GenericFormTemplate()
    application_id = form.application.data
    api = g.user.get_api()
    if 0 < application_id:
        application = api.get_entity_by_id(int(application_id))
        configuration = api.get_configuration(config.default_configuration)
        server_list = application.get_linked_entities(entity.Entity.HostRecord)
        entities = []
        for s in server_list:
            entities.append(s)
            state = s.get_property('State')
            addresses = ''
            if state == 'Primary':
                addresses = s.get_property('Secondary')
                s.set_property('State', 'Secondary')
            else:
                addresses = s.get_property('Primary')
                s.set_property('State', 'Primary')
            s.set_property('addresses', addresses)
            s.update()
            
        if len(entities):
            api.selective_deploy_synchronous(entities, properties='scope=related')
            
        # Put form processing code here
        text=get_resource_text()
        g.user.logger.info('SUCCESS')
        flash(text['success'], 'succeed')
        return redirect(url_for('flip_normal_drflip_normal_dr_flip_normal_dr_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'flip_normal_dr_page.html',
            form=form,
            text=get_resource_text(),
            options=g.user.get_options(),
        )

@route(app, '/flip_normal_dr/applications/<application_id>/servers')
@util.workflow_permission_required('flip_normal_dr_page')
@util.exception_catcher
def get_servers(application_id):
    servers = []
    application = g.user.get_api().get_entity_by_id(int(application_id))
    for s in application.get_linked_entities(entity.Entity.HostRecord):
        server = {}
        server['id'] = s.get_id()
        server['fqdn'] = s.get_full_name()
        server['state'] = s.get_property('State')
        server['addresses'] = s.get_property('addresses')
        servers.append(server)
    return jsonify(servers)
