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
# Date: 2020-12-16
# Gateway Version: 20.3.1
# Description: Example Gateway workflow

"""
Component logic
"""
from flask import g
from flask import jsonify
from flask import request

from main_app import app
from bluecat import entity
from bluecat import route
from bluecat.util import rest_exception_catcher
from bluecat.util import rest_workflow_permission_required
from bluecat.server_endpoints import empty_decorator
from bluecat.server_endpoints import get_result_template


def raw_table_data(*args, **kwargs):
    """Returns table formatted data for display in the TableField component."""
    # pylint: disable=unused-argument
    return {
        "columns": [
            {"title": "id"},
            {"title": "name"},
            {"title": "type"},
        ],
        "data": [
            [18371164, "All", "CUSTOM"],
            [18371166, "None", "CUSTOM"],
            [18371168, "Localhost", "CUSTOM"],
            [18371170, "Localnetworks", "CUSTOM"],
        ]
    }


def get_object_types(default_val=False):
    """Return all implemented Entity types formatted for a CustomSelectField"""
    result = []
    if g.user:
        if default_val:
            result.append(('1', 'Please Select'))

        for name, data in entity.Entity.__dict__.items():
            if not isinstance(data, str):
                continue
            if '__' in name[:2]:
                continue
            result.append((name, name))

    result.sort()

    return result

def raw_entities_to_table_data(entities):
    """
    Convert raw entities from a direct API call into table data of the form:
    data = {
        "columns": [
            {"title": "Heading1"},
            {"title": "Heading2"}
        ],
        "data": [
            ["dat1", "dat2"],
            ["dat3", "dat4"]
        }
    }
    Where the length of each list in data['data'] must equal to the number of columns

    :param entities: Response object containing entities from a direct API call
    :param return: Dictionary of data parsable by the UI Table Componenent
    """
    # pylint: disable=redefined-outer-name
    data = {'columns': [{'title': 'id'},
                        {'title': 'name'},
                        {'title': 'type'},],
            'data': []}

    # Iterate through each entity
    for entity in entities:
        data['data'].append([entity.get_id(), entity.name, entity.get_type()])

    return data

def find_objects_by_type_endpoint(workflow_name, element_id, permissions, result_decorator=None):
    """Endpoint for retrieving the selected objects"""
    # pylint: disable=unused-argument
    endpoint = 'find_objects_by_type'
    function_endpoint = '%sfind_objects_by_type' % workflow_name
    view_function = app.view_functions.get(function_endpoint)
    if view_function is not None:
        return endpoint
    if not result_decorator:
        result_decorator = empty_decorator

    g.user.logger.info('Creating endpoint %s', endpoint)

    @route(app, '/%s/%s' % (workflow_name, endpoint), methods=['POST'])
    @rest_workflow_permission_required(permissions)
    @rest_exception_catcher
    # pylint: disable=unused-variable
    def find_objects_by_type():
        """Retrieve a list of properties for the table"""
        # pylint: disable=broad-except
        try:
            keyword = request.form['keyword']
            object_type = request.form['object_type']

            # Get entities based on the selection
            entities = g.user.get_api().get_by_object_types(keyword, object_type)

            # Parse response object into table data
            data = raw_entities_to_table_data(entities)

            # If no entities were found reutrn with failure state and message
            result = get_result_template()
            if len(data['data']) == 0:
                result['status'] = 'FAIL'
                result['message'] = 'No entities of type "{TYPE}" were found.'.format(TYPE=object_type)
            else:
                result['status'] = 'SUCCESS'
            result['data'] = {"table_field": data}
            return jsonify(result_decorator(result))

        except Exception as e:
            result = get_result_template()
            result['status'] = 'FAIL'
            result['message'] = str(e)
            return jsonify(result_decorator(result))

    return endpoint


def server_table_data_endpoint(workflow_name, element_id, permissions, result_decorator=None):
    """Endpoint for server table data"""
    # pylint: disable=unused-argument
    endpoint = 'server_table_data'
    function_endpoint = '%sserver_table_data' % workflow_name
    view_function = app.view_functions.get(function_endpoint)
    if view_function is not None:
        return endpoint
    if not result_decorator:
        result_decorator = empty_decorator

    g.user.logger.info('Creating endpoint %s', endpoint)

    @route(app, '/%s/%s' % (workflow_name, endpoint), methods=['POST'])
    @rest_workflow_permission_required(permissions)
    @rest_exception_catcher
    # pylint: disable=unused-variable
    def server_table_data():
        """Retrieve server side table data"""
        keyword = request.form['keyword']
        object_type_id = request.form['object_type']

        response = get_result_template()
        response['status'] = 'SUCCESS'
        response['message'] = 'Retrieved server side table data'
        response['data'] = {
            'table_field': {
                'searching': False,
                'paging': False,
                'ordering': False,
                'info': False,
                'lengthChange': False,
                'columns': [
                    {'title': 'keyword'},
                    {'title': 'object_type'}
                ],
                'data': [
                    [keyword, object_type_id],
                ]
            }
        }
        return jsonify(result_decorator(response))

    return endpoint
