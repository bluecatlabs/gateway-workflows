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
# Description: Bulk Register User Page

# Various Flask framework items.
import os
import sys

from flask import url_for, redirect, render_template, flash, g, request, jsonify

from bluecat import route, util, user
import config.default_config as config
from main_app import app

from .bulk_register_user_form import get_resource_text
from .bulk_register_user_form import GenericFormTemplate


# No updateUserPassword method on user class yet.
def update_password(user, password):
    options = []
    try:
        user._api_client.service.updateUserPassword(user.get_id(), password, options)
    except WebFault as e:
        print('Exception at update_password(%s)' % util.safe_str(e))
        raise BAMException(safe_str(e))

def register_user(api, user_list):
    for line in user_list:
        user_name = line[0]
        password = line[1]
        email = line[2]
        last_name = line[3]
        first_name = line[4]
        user_type = line[5]
        access_type = line[6]
        
        print('Finding User %s' % user_name)

        try:
            user = api.get_user(user_name)
            print('Found user(%s) id(%d)' % (user_name, user.get_id()))
            if 0 < len(email):
                user.set_property('email', email)
            if 0 < len(last_name):
                user.set_property('LastName', last_name)
            if 0 < len(first_name):
                user.set_property('FirstName', first_name)
            if 0 < len(access_type):
                user.set_property('userAccessType', access_type)
            user.update()
            
            if 0 < len(password):
                update_password(user, password)
            
        except Exception as e:
            print('Exception %s' % util.safe_str(e))
            properties = ''
            if 0 < len(last_name):
                properties += 'LastName=' + last_name
            if 0 < len(first_name):
                properties += '|FirstName=' + first_name
            if 0 < len(user_type):
                properties += '|userType=' + user_type
            print('Adding User %s' % user_name)
            user = api.add_user(user_name, password, email, access_type, properties)


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/bulk_register_user/bulk_register_user_endpoint', methods=['GET', 'POST'])
@util.workflow_permission_required('bulk_register_user_page')
@util.exception_catcher
def bulk_register_user_bulk_register_user_page():
    form = GenericFormTemplate()
    return render_template(
        'bulk_register_user_page.html',
        form=form,
        text=get_resource_text(),
        options=g.user.get_options(),
    )

@route(app, '/bulk_register_user/submit_bulk_user_list', methods=['POST'])
@util.workflow_permission_required('bulk_register_user_page')
@util.exception_catcher
def bulk_register_user_submit_bulk_user_list():
    user_list = request.get_json()  
    register_user(g.user.get_api(), user_list)
    
    text=get_resource_text()
    g.user.logger.info('SUCCESS')
    flash(text['success'], 'succeed')
    return jsonify('', 200)
