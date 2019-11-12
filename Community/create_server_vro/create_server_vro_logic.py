# Copyright 2019 BlueCat Networks. All rights reserved.
from flask import g, request, jsonify

from main_app import app
from bluecat import route
import bluecat_portal.config as config
from bluecat.util import rest_exception_catcher
from bluecat.util import rest_workflow_permission_required
from bluecat.util import has_response
from bluecat.util import safe_str
from bluecat.util import properties_to_map, is_valid_ipv4_address
from bluecat.api_exception import PortalException, BAMException
from bluecat.server_endpoints import empty_decorator, get_result_template


SUCCESS = 'SUCCESS'
FAIL = 'FAIL'


# pylint: disable=unused-argument
def get_ip4_networks_endpoint(workflow_name, element_id, permissions, result_decorator=None):
    """
    Generate an endpoint for retrieving IP4 networks by hint

    Returns: A list of networks for autocomplete field

    :param workflow_name: The name of the workflow that is using this endpoint.
    :param element_id: The ID of the form field using this endpoint.
    :param permissions: What workflow permissions the user needs to access this endpoint.
    :param result_decorator: function to add custom manipulations to a result set.
    :return: The generated endpoint unique to get_zones_endpoint.
    """
    endpoint = 'get_ip4_networks'
    function_endpoint = '%sget_ip4_networks' % workflow_name
    view_function = app.view_functions.get(function_endpoint)
    if view_function is not None:
        return endpoint

    if not result_decorator:
        result_decorator = empty_decorator

    @route(app, '/%s/%s' % (workflow_name, endpoint), methods=['POST'])
    @rest_workflow_permission_required(permissions)
    @rest_exception_catcher
    # pylint: disable=unused-variable
    def get_ip4_networks():
        """
        Exposed endpoint for retrieving networks by hint.
        Used for populating autocomplete fields, does not return all information.
        """
        hint = request.form['ip4_network']
        return jsonify(result_decorator(get_ip4_networks_data(hint)))
    return endpoint


def get_ip4_networks_data(hint):
    """
    Get a list of networks that corresponds to the configuration and hint entered by the user
    :param hint: Network hint to search with
    :return: networks that correspond to the network hint
    """
    # Use the default result template
    result = get_result_template()
    result['data']['autocomplete_field'] = []

    # Retrieve the configuration
    try:
        configuration_id = request.form['configuration']
    except PortalException as e:
        result['status'] = FAIL
        g.user.logger.warning('%s' % e, msg_type=g.user.logger.EXCEPTION)
        return result

    # Retrieve network based on user input
    try:
        networks = g.user.get_api()._api_client.service.getIP4NetworksByHint(configuration_id, 0, 5, 'hint=%s' % hint)
    except BAMException as e:
        result['status'] = FAIL
        g.user.logger.warning('%s' % e, msg_type=g.user.logger.EXCEPTION)
        result['message'] = 'Unable to retrieve network with error %s: ' % safe_str(e)
        return result

    if has_response(networks):
        for network in networks.item:
            network = g.user.get_api().instantiate_entity(network)
            network_string = network.get_property('CIDR')
            result['data']['autocomplete_field'].append({"value": network_string})

    result['status'] = SUCCESS
    return result
