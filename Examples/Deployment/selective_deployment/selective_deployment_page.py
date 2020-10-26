# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates
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
# Date: 2020-11-26
# Gateway Version: 20.3.1
# Description: Example Gateway workflow

"""this file is responsible to selective deploying certain dns records
and retrieving the result"""
import os

from flask import jsonify

from flask import render_template, g, request

from bluecat import route, util
from bluecat.server_endpoints import get_result_template
from bluecat.server_endpoints import empty_decorator
from bluecat.constants import SelectiveDeploymentStatus

import config.default_config as config
from main_app import app
from .component_logic import raw_entities_to_table_data

from .selective_deployment_form import GenericFormTemplate


def module_path():
    """module path"""
    return os.path.dirname(os.path.abspath(str(__file__)))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/selective_deployment/selective_deployment_endpoint')
@util.workflow_permission_required('selective_deployment_page')
@util.exception_catcher
def selective_deployment_selective_deployment_page():
    # pylint: disable=invalid-name
    """render the html page for selective deployment"""
    form = GenericFormTemplate()
    return render_template(
        'selective_deployment_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )


@route(app, '/selective_deployment/update_objects', methods=['POST'])
@util.rest_workflow_permission_required('selective_deployment_page')
@util.rest_exception_catcher
def update_objects():
    """checks the status of task and transfer the results to the table"""
    try:
        key = request.form['message']
        status = g.user.get_api().get_deployment_task_status(key)

        entity_status = {}
        dns_records_list = request.form['dns_records_list'].split('.')
        deployment_error = ''
        for record_id in dns_records_list:
            entity_status[record_id] = '<font color = yellow> '+status['status']+' </font>'
            if status['status'] == SelectiveDeploymentStatus.FINISHED:
                entity_status[record_id] = 'Already deployed and not modified'
                if status['response']['errors']:
                    deployment_error = 'ERROR Selective Deployment: ' + \
                                       status['response']['errors'][0]
                    entity_status[record_id] = \
                        '<font color = red>ERROR: See logs for details</font>'
                elif status['response']['views']:
                    try:
                        for records in status['response']['views'][0]['zones'][0]['records']:
                            if str(records['id']) == str(record_id):
                                color = '#cb4814'
                                if records['result'] == SelectiveDeploymentStatus.FAILED:
                                    color = 'red'
                                elif records['result'] == SelectiveDeploymentStatus.SUCCEEDED:
                                    color = '#76ce66'
                                entity_status[record_id] = '<font color = %s>' % color + \
                                                           records['result'] + '</font>'
                                app.logger.info(record_id + ' Status : ' + entity_status[record_id])
                    except IndexError as error:
                        entity_status[record_id] = '<font color = red> ERROR: '\
                                           + str(error) + ', Could not find the results </font>'
        if deployment_error != '':
            app.logger.error(deployment_error)

        data = raw_entities_to_table_data(entity_status, False)
        result = get_result_template()
        data['columnDefs'] = [{'targets': [3], 'render': ''}]
        result['status'] = status['status']
        result['data'] = {"table_field": data,
                          "message": '%s' % key,
                          "configuration": request.form['configuration'],
                          "view": request.form['view'],
                          "zone": request.form['zone'],
                          "dns_records_list": request.form['dns_records_list']}
    # pylint: disable=broad-except
    except Exception as e:
        result = get_result_template()
        result['status'] = 'FAIL'
        result['message'] = util.safe_str(e)
        return jsonify(empty_decorator(result))

    return jsonify(empty_decorator(result))


@route(app, '/selective_deployment/deploy_objects', methods=['POST'])
@util.rest_workflow_permission_required('selective_deployment_page')
@util.rest_exception_catcher
def deploy_objects():
    """Retrieve a list of user selected host records and passes it to the update function"""

    selected_list = []
    dns_records_list = ''
    try:
        for key in request.form:
            try:
                if key.isdigit() and request.form['%s' % key] == 'on':
                    selected_list.append(key)
            except AttributeError:
                if request.form[key] == 'on':
                    selected_list.append(key)

        token = g.user.get_api().selective_deploy(selected_list, 'scope=related')
        status = g.user.get_api().get_deployment_task_status(token)

        for record_id in selected_list:
            dns_records_list = dns_records_list + '%s.' % record_id

        dns_records_list = dns_records_list[:-1]
        result = get_result_template()
        result['status'] = '%s' % status['status']
        result['data'] = {"message": '%s' % token,
                          "configuration": request.form['configuration'],
                          "view": request.form['view'],
                          "zone": request.form['zone'],
                          "dns_records_list": dns_records_list}
        g.user.logger.info(token)
    # pylint: disable=broad-except
    except Exception as e:
        result = get_result_template()
        result['status'] = 'FAIL'
        result['message'] = util.safe_str(e)
        return jsonify(empty_decorator(result))

    return jsonify(empty_decorator(result))
