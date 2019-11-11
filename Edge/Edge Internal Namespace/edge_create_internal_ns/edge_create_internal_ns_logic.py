# Copyright 2019 BlueCat Networks. All rights reserved.
from flask import request

from main_app import app
from bluecat import route, util
from bluecat.util import rest_exception_catcher
from bluecat.util import rest_workflow_permission_required
from bluecat.server_endpoints import empty_decorator
from bluecat_portal.customizations.edge import edge
from ..edge_create_internal_ns_config import edge_create_internal_ns_configuration

FAIL = 'FAIL'
SUCCESS = 'SUCCESS'


def get_edge_namespaces_endpoint(workflow_name, element_id, permissions, result_decorator=None):
    """
    Generate an endpoint for retrieving IP4 networks by hint

    Returns: A list of networks for autocomplete field

    :param workflow_name: The name of the workflow that is using this endpoint.
    :param element_id: The ID of the form field using this endpoint.
    :param permissions: What workflow permissions the user needs to access this endpoint.
    :param result_decorator: function to add custom manipulations to a result set.
    :return: The generated endpoint unique to get_zones_endpoint.
    """
    endpoint = 'get_edge_namespaces'
    function_endpoint = '%sget_edge_namespaces' % workflow_name
    view_function = app.view_functions.get(function_endpoint)
    if view_function is not None:
        return endpoint

    if not result_decorator:
        result_decorator = empty_decorator

    @route(app, '/%s/%s' % (workflow_name, endpoint), methods=['POST'])
    @rest_workflow_permission_required(permissions)
    @rest_exception_catcher
    # pylint: disable=unused-variable
    def get_edge_namespaces():
        """
        Exposed endpoint for retrieving networks by hint.
        Used for populating autocomplete fields, does not return all information.
        """
        hint = request.form['namespaces']

        result = {'status': FAIL, 'message': '', 'data': {}}
        try:
            result['status'] = SUCCESS
            result['data']['autocomplete_field'] = []
            result['data']['select_field'] = []
            if hint != '':
                edge_session = edge(edge_create_internal_ns_configuration.edge_url,
                                    edge_create_internal_ns_configuration.client_id,
                                    edge_create_internal_ns_configuration.clientSecret)

                namespaces = edge_session.get_namespaces()
                count = 0
                for namespace in namespaces:
                    if namespace['name'].startswith(hint):

                        result['data']['autocomplete_field'].append({
                            'input': namespace['id'],
                            'value': '%s (%s)' % (namespace['name'], namespace['id'])
                        })
                        result['data']['select_field'].append({
                            'id': namespace['id'],
                            'txt': namespace['name']
                        })
                        if count == 10:
                            break
                        count += 1
        except Exception as e:
            result['status'] = FAIL
            result['message'] = 'Error while searching for Namespaces: %s and hint: %s!' % (util.safe_str(e), hint)
        return result

    return endpoint
