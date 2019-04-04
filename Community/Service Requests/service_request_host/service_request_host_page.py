# Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
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
import os
import sys
import time

import requests
from flask import url_for, redirect, render_template, flash, g, request, jsonify, json

from main_app import app
from bluecat import route, util
import config.default_config as config
from bluecat.constants import IPAssignmentActionValues
from bluecat.api_exception import PortalException, BAMException
from .service_request_host_form import GenericFormTemplate
from bluecat.server_endpoints import get_result_template, empty_decorator
from .service_request_host_config import ServiceRequestHostConfig


headers = {"Content-Type": "application/json", "Accept": "application/json"}


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/service_request_host/service_request_host_endpoint')
@util.workflow_permission_required('service_request_host_page')
@util.exception_catcher
def service_request_host_page():
    """
    Renders the form the user would first see when selecting the workflow.
    :return:
    """
    form = GenericFormTemplate()
    return render_template(
        'service_request_host_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options()
    )


@route(app, '/service_request_host/form', methods=['POST'])
@util.workflow_permission_required('service_request_host_page')
@util.exception_catcher
def service_request_host_page_form():
    """
    Processes the final form after the user has input all the required data.
    :return:
    """
    form = GenericFormTemplate()
    ip4_address_list = []

    # Retrieve the configuration object
    try:
        configuration = g.user.get_api().get_configuration(config.default_configuration)
        view = configuration.get_view(config.default_view)
        configuration.assign_ip4_address(form.ip4_address.data, '', '', IPAssignmentActionValues.MAKE_RESERVED)
    except PortalException as e:
        g.user.logger.error('%s' % e, msg_type=g.user.logger.EXCEPTION)
        flash('Unable to retrieve configuration or view specified in configuration')
        return redirect(url_for('service_request_hostservice_request_host_page'))

    # Retrieve form attributes
    absolute_name = form.hostname.data + '.' + request.form['zone']
    ip4_address_list.append(form.ip4_address.data)

    # This is the field that we will pass the requested information to in ServiceNow
    ticket_information = {
        'short_description': 'BlueCat: Ticket requested to create %s with host record %s' % (ip4_address_list[0], absolute_name),
        'description': 'configuration=%s, view=%s, host_record=%s, ip_address=%s'
                       % (configuration.get_name(), view.get_name(), absolute_name, ip4_address_list[0]),
        'assigned_to': 'admin',
        'category': 'network',
        'comments': 'Created from BlueCat Gateway / API'
    }

    # Do the HTTP request
    response = requests.post(ServiceRequestHostConfig.servicenow_url,
                             auth=(ServiceRequestHostConfig.servicenow_username, ServiceRequestHostConfig.servicenow_password),
                             headers=headers,
                             data=json.dumps(ticket_information),
                             verify=False)
    time.sleep(5)

    if response.status_code != 201:
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.json())
        exit()

    # Put form processing code here
    flash('Successfully created ServiceNow Ticket: ' + response.json()['result']['number'], 'succeed')
    flash('')
    return redirect(url_for('service_request_hostservice_request_host_page'))
