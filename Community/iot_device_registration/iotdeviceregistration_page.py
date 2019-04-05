#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
# By: Muhammad Heidir (mheidir@bluecatnetworks.com)
# Date: 03-04-2019
# Gateway Version: 18.10.2
# Description: Bulk IoT Device Registration/De-Registration workflow for BlueCat Gateway

# Various Flask framework items.
import os
import sys
import codecs
import io
import csv
from os import system

from flask import url_for, redirect, render_template, flash, g, jsonify
from werkzeug.utils import secure_filename

from bluecat import route, util
import config.default_config as config
from main_app import app
from .iotdeviceregistration_form import GenericFormTemplate

from .checkiotexpiration_v1 import check_iot_expiration
from .iotipallocation_v2 import iot_ip_allocation

def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/iotdeviceregistration/iotdeviceregistration_endpoint')
@util.workflow_permission_required('iotdeviceregistration_page')
@util.exception_catcher
def iotdeviceregistration_iotdeviceregistration_page():
    form = GenericFormTemplate()
    return render_template(
        'iotdeviceregistration_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

def form_validation(form, filebuf):
    valid = False
    
    if False == form.validate_on_submit():
        g.user.logger.info('Form data was not valid.')
    elif filebuf is None or filebuf == '':
        g.user.logger.info('File was not set.')
        flash('File was not set.')
    #elif 'text/plain' != filebuf.mimetype:
    elif filebuf.mimetype not in ('text/csv', 'application/vnd.ms-excel'):
        g.user.logger.info('Only CSV file is allowed.')
        g.user.logger.info(filebuf.mimetype)
        flash('Only CSV file is allowed.')
    else:
        valid = True
    return valid

@route(app, '/iotdeviceregistration/form', methods=['POST'])
@util.workflow_permission_required('iotdeviceregistration_page')
@util.exception_catcher
def iotdeviceregistration_iotdeviceregistration_page_form():
    form = GenericFormTemplate()
    filebuf = form.file.data
    if form_validation(form, filebuf):
        file_name = secure_filename(filebuf.filename)
        file_path = os.path.join(module_path(), file_name)
        filebuf.save(file_path)
        
        # Put form processing code here
        g.user.logger.info("Processing IOT Device registration")
        iot_ip_allocation(file_path, form.name.data, form.email.data)
        g.user.logger.info("End of processing")
        flash('IoT Devices successfully processed. Please check email for the status and detailed information', 'succeed')
        return redirect(url_for('iotdeviceregistrationiotdeviceregistration_iotdeviceregistration_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'iotdeviceregistration_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )

@route(app, '/iotdeviceregistration/checkiotexpiration', methods=['GET'])
@util.workflow_permission_required('iotdeviceregistration_page')
@util.exception_catcher
def iotdeviceregistration_checkiotexpiration_page():
    """ Executes scheduled clean-up of expired IoT device registrations """
    try:
        result = check_iot_expiration()
        return jsonify(result), 200
    except Exception as err:
        g.user.logger.error(err)
        g.user.logger.debug(traceback.print_exc(limit=5))
        return jsonify(str(err)), 500
