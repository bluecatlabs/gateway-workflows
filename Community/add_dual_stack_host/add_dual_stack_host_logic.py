# Copyright 2020 BlueCat Networks. All rights reserved.
from flask import g, request, jsonify

from main_app import app
from bluecat import route, util
from bluecat.entity import Entity
import bluecat_portal.config as config
from bluecat.util import rest_exception_catcher
from bluecat.util import rest_workflow_permission_required
from bluecat.util import is_valid_ipv6_address
from bluecat.api_exception import PortalException
from bluecat.server_endpoints import empty_decorator, get_result_template
import logging
logging.basicConfig(level=logging.DEBUG)

SUCCESS = 'SUCCESS'
FAIL = 'FAIL'

def get_ip6_address_endpoint(workflow_name, element_id, permissions, result_decorator=None):
    """
    Generate an endpoint for retrieving IP6 Address data. Accepts the following keys in the posted form:
    configuration, address.

    Where:
        configuration - The ID of the configuration containing the IPv6 Address.

        address - The IP of the IPv6 Address.

    Returns:
        IP6 object with status, name and MAC address properties if it is a valid address within a network.

    :param workflow_name: The name of the workflow that is using this endpoint.
    :param element_id: The ID of the form field using this endpoint.
    :param permissions: What workflow permissions the user needs to access this endpoint.
    :param result_decorator: Function to add custom manipulations to a result set.
    :return: The generated endpoint unique to get_ip6_address_endpoint.
    """

    endpoint = 'get_ip6_address'
    function_endpoint = '%sget_ip6_address' % workflow_name
    view_function = app.view_functions.get(function_endpoint)
    if view_function is not None:
        return endpoint

    if not result_decorator:
        result_decorator = empty_decorator


    @route(app, '/%s/%s' % (workflow_name, endpoint), methods=['GET', 'POST'])
    @rest_workflow_permission_required(permissions)
    @rest_exception_catcher
    # pylint: disable=unused-variable
    def get_ip6_address():
        """
        Exposed endpoint for retrieving an IP6 address.
        :return: All data in the BAM about the IP6 address.
        """
        if request.method == 'POST':
            configuration_id = request.form['configuration']
            ip6_address = request.form['ip6_address']
            return jsonify(result_decorator(get_address_data(configuration_id, ip6_address)))

    return endpoint


def get_address_data(configuration_id, ip6_address):
    """
    Get the BAM data for a given ip6_address in the given configuration.

    :param configuration_id: The ID of the configuration in which the ip6_address resides.
    :param ip6_address: The IP address in string form.
    :return: The IP address data in JSON, using result template format.
    """

    # Regular expression to match IPv6 format
    result = get_result_template()
    if not is_valid_ipv6_address(ip6_address):
        result['message'] = 'IP address is invalid.'
        result['status'] = FAIL
        return result

    # Retrieve the configuration object
    configuration = g.user.get_api().get_entity_by_id(configuration_id)

    # Check if IP address exists within a network. Fail if not.
    try:
        configuration.get_ip_ranged_by_ip(Entity.IP6Network, ip6_address)
        result['message'] = 'IPv6 Address is available'
        result['status'] = SUCCESS
        result['data'] = {
            'state': None,
            'mac_address': None,
            'name': None
        }
        return result
    except PortalException:
        result['message'] = 'IP address is not in a network or network does not exist'
        result['status'] = FAIL
        return result
