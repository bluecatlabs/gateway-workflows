# Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
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
# Description: Query Unused MAC Address Page

# Various Flask framework items.
import os
import sys

from flask import url_for, redirect, render_template, flash, g

from bluecat import route, util
from main_app import app

from .query_unused_mac_address_access import get_resource_text
from .query_unused_mac_address_form import GenericFormTemplate

# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/query_unused_mac_address/query_unused_mac_address_endpoint')
@util.workflow_permission_required('query_unused_mac_address_page')
@util.exception_catcher
def query_unused_mac_address_query_unused_mac_address_page():
    form = GenericFormTemplate()
    return render_template(
        'query_unused_mac_address_page.html',
        form=form,
        text=get_resource_text(),
        options=g.user.get_options(),
    )

@route(app, '/query_unused_mac_address/form', methods=['POST'])
@util.workflow_permission_required('query_unused_mac_address_page')
@util.exception_catcher
def query_unused_mac_address_query_unused_mac_address_page_form():
    form = GenericFormTemplate()
    if form.validate_on_submit():
        # Put form processing code here
        g.user.logger.info('SUCCESS')
        flash('success', 'succeed')
        return redirect(url_for('query_unused_mac_addressquery_unused_mac_address_query_unused_mac_address_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'query_unused_mac_address_page.html',
            form=form,
            text=get_resource_text(),
            options=g.user.get_options(),
        )
