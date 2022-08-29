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
# Date: 2020-12-15
# Gateway Version: 20.12.1
# Description: Bulk Deletion MAC Address Page

from flask import request, render_template, flash, jsonify, g

from bluecat import route, util
import config.default_config as config
from main_app import app
from .bulk_delete_mac_address_form import GenericFormTemplate

from .bulk_delete_mac_address_form import get_resource_text
from .migration import delete_mac_address

def get_configuration(api, config_name):
    configuration = api.get_configuration(config_name)
    return configuration


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/bulk_delete_mac_address/bulk_delete_mac_address_endpoint')
@util.workflow_permission_required('bulk_delete_mac_address_page')
@util.exception_catcher
@util.ui_secure_endpoint
def bulk_delete_mac_address_bulk_delete_mac_address_page():
    form = GenericFormTemplate()
    return render_template(
        'bulk_delete_mac_address_page.html',
        form=form,
        text=get_resource_text(),
        options=g.user.get_options(),
    )

@route(app, '/bulk_delete_mac_address/submit_bulk_mac_address_list', methods=['POST'])
@util.workflow_permission_required('bulk_delete_mac_address_page')
@util.exception_catcher
def bulk_delete_mac_address_bulk_delete_mac_address_page_submit_bulk_mac_address_list():
    mac_address_list = request.get_json()
    print('Size of mac_address_list %d' % len(mac_address_list))
    configuration = get_configuration(g.user.get_api(), config.default_configuration)
    for line in mac_address_list:
        address = str(line[0])
        delete_mac_address(configuration, address)
        
    text=get_resource_text()
    g.user.logger.info('SUCCESS')
    flash(text['success'], 'succeed')
    return jsonify('', 200)

















# @route(app, '/bulk_delete_mac_address/form', methods=['POST'])
# @util.workflow_permission_required('bulk_delete_mac_address_page')
# @util.exception_catcher
# @util.ui_secure_endpoint
# def bulk_delete_mac_address_bulk_delete_mac_address_page_form():
#     form = GenericFormTemplate()
#     # Remove this line if your workflow does not need to select a configuration
#     form.configuration.choices = util.get_configurations(default_val=True)
#     if not form.validate_on_submit():
#         g.user.logger.info('Form data was not valid.')
#         return render_template(
#             'bulk_delete_mac_address_page.html',
#             form=form,
#             text=util.get_text(module_path(), config.language),
#             options=g.user.get_options(),
#         )

#     print(form.configuration.data)
#     print(form.email.data)
#     print(form.password.data)
#     print(form.mac_address.data)
#     print(form.ip_address.data)
#     print(form.url.data)
#     print(form.file.data)
#     print(form.boolean_checked.data)
#     print(form.boolean_unchecked.data)
#     print(form.date_time.data)
#     print(form.submit.data)

#     # Put form processing logic here
#     g.user.logger.info('SUCCESS')
#     flash('success', 'succeed')
#     return redirect(url_for('bulk_delete_mac_addressbulk_delete_mac_address_bulk_delete_mac_address_page'))
