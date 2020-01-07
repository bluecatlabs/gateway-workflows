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
# Description: Bulk Register Group Page

# Various Flask framework items.
import os
import sys

from flask import url_for, redirect, render_template, flash, g, request, jsonify

from bluecat import route, util, user_group
import config.default_config as config
from main_app import app

from .bulk_register_group_form import get_resource_text
from .bulk_register_group_form import GenericFormTemplate

def register_group(api, group_list):
    for line in group_list:
        group_name = line[0]
        division_code = line[1]
        comments = line[2]
        
        try:
            group = api.get_group(group_name)
            #print('Found group(%s) id(%d)' % (group_name, group.get_id()))
            if 0 < len(division_code):
                group.set_property('DivisionCode', division_code)
            if 0 < len(comments):
                group.set_property('Comments', comments)
            group.update()
                        
        except Exception as e:
            print('Exception %s' % util.safe_str(e))
            properties = 'isAdministrator=false'
            if 0 < len(division_code):
                properties += '|DivisionCode=' + division_code
            if 0 < len(comments):
                properties += '|Comments=' + comments
            #print('Adding group %s' % group_name)
            group = api.add_group(group_name, properties)


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/bulk_register_group/bulk_register_group_endpoint', methods=['GET', 'POST'])
@util.workflow_permission_required('bulk_register_group_page')
@util.exception_catcher
def bulk_register_group_bulk_register_group_page():
    print('bulk_register_group_bulk_register_group_page is called!!!!')
    form = GenericFormTemplate()
    return render_template(
        'bulk_register_group_page.html',
        form=form,
        text=get_resource_text(),
        options=g.user.get_options(),
    )

@route(app, '/bulk_register_group/submit_bulk_group_list', methods=['POST'])
@util.workflow_permission_required('bulk_register_group_page')
@util.exception_catcher
def bulk_register_group_bulk_register_group_page_submit_bulk_group_list():
    group_list = request.get_json()  
    register_group(g.user.get_api(), group_list)

    text=get_resource_text()
    g.user.logger.info('SUCCESS')
    flash(text['success'], 'succeed')
    return jsonify('', 200)
