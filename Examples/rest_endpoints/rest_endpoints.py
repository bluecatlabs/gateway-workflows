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
# Date: 2020-08-31
# Gateway Version: 20.1.1
# Description: Example Gateway workflow

"""
REST example workflow
"""
from flask import request, g, jsonify

from bluecat import route, util
from main_app import app


def autologin_func():
    """
    I strongly recommend in real scenario use something more secure than storing plain text
    username and password in a workflow file.
    :return: username and password
    """
    return 'testuser', 'testuser'


def get_configurations():
    """
    A simple example that connects to BAM and retrieves a list of configurations
    :return: List of BAM configurations
    """
    res = {}
    res['username'] = g.user.get_username()
    configs = []
    for c in g.user.get_api().get_configurations():
        configs.append({'id': c.get_id(), 'name': c.get_name()})
    res['configs'] = configs
    return jsonify(res)

#
# Example rest GET call
#
@route(app, '/rest_endpoints/get_test')
@util.rest_workflow_permission_required('rest_endpoints')
@util.rest_exception_catcher
def rest_get_test():
    """
    GET call

    :return:
    """
    # are we authenticated?
    # yes, build a simple JSON response
    return get_configurations()


#
# Example rest PUT call
#
@route(app, '/rest_endpoints/put_test', methods=['PUT'])
@util.rest_workflow_permission_required('rest_endpoints')
@util.rest_exception_catcher
def rest_put_test():
    """
    PUT call

    :return:
    """
    return jsonify({'result': request.get_json()['foo'] + ' plus some extra'})


#
# Autologin Example
#
@route(app, '/rest_endpoints/list_configurations', methods=['GET', 'POST'])
@util.autologin(autologin_func)
@util.rest_exception_catcher
def rest_test_autologin():
    """
    Autologin

    :return:
    """
    # in this case it is always executed
    return get_configurations()


#
# Example of an endpoint with no authentication required
#
@route(app, '/rest_endpoints/no_auth_test')
@util.rest_exception_catcher
def rest_test_no_auth():
    """
    Endpoint with no authentication

    :return:
    """
    # Permission check is not applicable here
    return jsonify({'answer': 42})
