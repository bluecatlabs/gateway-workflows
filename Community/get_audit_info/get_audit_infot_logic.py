
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
import config.default_config as config

def raw_table_data(*args, **kwargs):
    """Returns table formatted data for display in the TableField component"""
    # pylint: disable=unused-argument
    return {
        "columns": [
            {"title": "Date"},
            {'title': 'Transaction Number'},
            {'title': 'Comment'},
            {'title': 'Type'},
            {'title': 'ObjectId'},
            {'title': 'Name'},
            {'title': 'User'},
            {'title': 'Machine IP'},
        ],
        "data": [

        ]
    }

def raw_entities_to_table_data(records):
    # pylint: disable=redefined-outer-name
    data = {'columns': [{'title': 'Date'},
                        {'title': 'Transaction Number'},
                        {'title': 'Comment'},
                        {'title': 'Type'},
                        {'title': 'ObjectId'},
                        {'title': 'Name'},
                        {'title': 'User'},
                        {'title': 'Machine IP'},],
            'data': []}

    # Iterate through each record
    for record in records:
        if record['type'] == 'I':
            record['type'] = 'Created'
        if record['type'] == 'U':
            record['type'] = 'Updated'
        if record['type'] == 'D':
            record['type'] = 'Deleted'
        else:
            record['type']

        data['data'].append([record['date'], record['transaction_number'], record['comment'], record['type'], record['object_id'], record['name'], record['user'], record['machine_ip']])

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

            # Valid units for interval:
            # millennium, century, decade, year, month, week, day, hour, minute, second, millisecond, microsecond

            form_interval = request.form['interval']
            logs = g.user.get_api().get_audit_logs(form_interval, transaction_id=None, descending=False)

            # Parse response object into table data
            data = raw_entities_to_table_data(logs)

            # If no entities were found return with failure state and message
            result = get_result_template()
            if len(data['data']) == 0:
                result['status'] = 'FAIL'
                result['message'] = 'No records  were found.'
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