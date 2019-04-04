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
def get_zones_endpoint(workflow_name, element_id, permissions, result_decorator=None):
    """
    Generate an endpoint for retrieving zone data. Accepts the following keys in the posted form:
    configuration, view, zone.

    Where:
        configuration - The ID of the configuration containing the Zone(s).
        view - The name of the view in the given configuration that contains the Zone(s).
        zone - The full name of the zone to find or partial name matching any number of zones.
    Returns:
        A list of zone paths for autocomplete field and a list of zone paths and zone id's for select field

    :param workflow_name: The name of the workflow that is using this endpoint.
    :param element_id: The ID of the form field using this endpoint.
    :param permissions: What workflow permissions the user needs to access this endpoint.
    :param result_decorator: Function to add custom manipulations to a result set.
    :return: The generated endpoint unique to get_zones_endpoint.
    """
    endpoint = 'get_zones'
    function_endpoint = '%sget_zones' % workflow_name
    view_function = app.view_functions.get(function_endpoint)
    if view_function is not None:
        return endpoint

    if not result_decorator:
        result_decorator = empty_decorator

    @route(app, '/%s/%s' % (workflow_name, endpoint), methods=['POST'])
    @rest_workflow_permission_required(permissions)
    @rest_exception_catcher
    # pylint: disable=unused-variable
    def get_zones():
        """
        Exposed endpoint for retrieving zones with a given hint in a view. Used for populating select fields, does not
        return all information.
        """
        hint = request.form['zone'].strip()
        return jsonify(result_decorator(get_zones_data(hint)))
    return endpoint


def get_zones_data(hint):
    """
    Get a list of zone FQDNs that corresponds to the given hint.

    :return: FQDN of any zones that match the given hint as data in JSON, using result template format.
    """
    # Declare variables
    result = get_result_template()
    result['data']['autocomplete_field'] = []

    # Retrieve the configuration and view object
    try:
        configuration = g.user.get_api().get_configuration(config.default_configuration)
        view = configuration.get_view(config.default_view)
    except PortalException as e:
        result['status'] = FAIL
        g.user.logger.warning('%s' % e, msg_type=g.user.logger.EXCEPTION)
        return result

    # If null user input then set hint to empty to pre-populate the dropdown, otherwise search with user input
    if safe_str(hint) == 'null':
        properties = 'hint=|'
    else:
        properties = 'hint=' + hint

    # Retrieve zones
    zones = g.user.get_api()._api_client.service.getZonesByHint(view.get_id(), 0, 5, properties)

    # If valid zones are retrieved then extract the absolute name and append to result
    if has_response(zones):
        for zone in zones.item:
            result['data']['autocomplete_field'].append(properties_to_map(zone['properties'])['absoluteName'])

    result['status'] = SUCCESS
    return result


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
        configuration_id = g.user.get_api().get_configuration(config.default_configuration).get_id()
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
            network_string = network.get_property('CIDR') + ' (' + safe_str(network.get_name()) + ')'
            result['data']['autocomplete_field'].append({"value": network_string, "label": network_string})

    result['status'] = SUCCESS
    return result

def get_next_ip4_address_endpoint(workflow_name, element_id, permissions, result_decorator=None):
    """
    Generate an endpoint that retrieves the next available IP4 address in the selected network.
    Accepts the network CIDR.

    Where:
        Network CIDR - User selected network CIDR
    Returns:
        Next available IPv4 addresses from the given CIDR

    :param workflow_name: The name of the workflow that is using this endpoint.
    :param element_id: The ID of the form field using this endpoint.
    :param permissions: What workflow permissions the user needs to access this endpoint.
    :param result_decorator: function to add custom manipulations to a result set.
    :return: The generated endpoint unique to get_zones_endpoint.
    """
    endpoint = 'get_next_ip4_address'
    function_endpoint = '%sget_next_ip4_address' % workflow_name
    view_function = app.view_functions.get(function_endpoint)
    if view_function is not None:
        return endpoint

    if not result_decorator:
        result_decorator = empty_decorator

    @route(app, '/%s/%s' % (workflow_name, endpoint), methods=['POST'])
    @rest_workflow_permission_required(permissions)
    @rest_exception_catcher
    # pylint: disable=unused-variable
    def get_next_ip4_address():
        """
        Exposed endpoint for retrieving the next available IP4 address
        Used for populating the IP4 address field
        """
        ip4_network = request.form['ip4_network']
        return jsonify(result_decorator(get_next_ip4_address_data(ip4_network)))
    return endpoint


def get_next_ip4_address_data(ip4_network):
    """
    Retrieve the next available IP4 Addresses given the network CIDR
    :param ip4_network: Network CIDR
    :return: Next available IP4 Address
    """
    # Endpoint presets
    result = get_result_template()

    # Retrieve the configuration
    try:
        configuration = g.user.get_api().get_configuration(config.default_configuration)
    except PortalException as e:
        result['status'] = FAIL
        g.user.logger.warning('%s' % e, msg_type=g.user.logger.EXCEPTION)
        return result

    # Network is in CIDR format, retrieve the network and the next available ipv4 address
    network = ip4_network.split('/')
    try:
        network = configuration.get_ip_range_by_ip('IP4Network', network[0])
    except BAMException as e:
        result['status'] = FAIL
        g.user.logger.warning('%s' % e, msg_type=g.user.logger.EXCEPTION)
        return result
    ipv4_address = network.get_next_ip4_address_string()

    if ipv4_address:
        result['status'] = SUCCESS
        result['data'] = [
            ipv4_address
        ]
    else:
        result['status'] = SUCCESS
        result['data'] = [
            'network is fully allocated'
        ]
    return result


def get_ip4_address_endpoint(workflow_name, element_id, permissions, result_decorator=None):
    """
    Generate an endpoint for retrieving IP4 Address data. Accepts the following keys in the posted form:
    configuration, address.

    Where:
        configuration - The ID of the configuration containing the IPv4 Address.

        address - The IP of the IPv4 Address.

    Returns:
        IP4 object with status, name and MAC address properties if it is a valid address within a network.

    :param workflow_name: The name of the workflow that is using this endpoint.
    :param element_id: The ID of the form field using this endpoint.
    :param permissions: What workflow permissions the user needs to access this endpoint.
    :param result_decorator: Function to add custom manipulations to a result set.
    :return: The generated endpoint unique to get_ip4_address_endpoint.
    """
    endpoint = 'get_address'
    function_endpoint = '%sget_address' % workflow_name
    view_function = app.view_functions.get(function_endpoint)
    if view_function is not None:
        return endpoint

    if not result_decorator:
        result_decorator = empty_decorator

    @route(app, '/%s/%s' % (workflow_name, endpoint), methods=['POST'])
    @rest_workflow_permission_required(permissions)
    @rest_exception_catcher
    # pylint: disable=unused-variable
    def get_address():
        """
        Exposed endpoint for retrieving an IP4 address.
        :return: All data in the BAM about the IP4 address.
        """
        configuration_id = 0
        ip4_address = request.form['address']
        return jsonify(result_decorator(get_address_data(configuration_id, ip4_address)))

    return endpoint


def get_address_data(configuration_id, ip4_address):
    """
    Get the BAM data for a given ip4_address in the given configuration.

    :param configuration_id: The ID of the configuration in which the ip4_address resides.
    :param ip4_address: The IP address in octet form.
    :return: The IP address data in JSON, using result template format.
    """
    result = get_result_template()
    if not is_valid_ipv4_address(ip4_address):
        result['message'] = 'IP address is invalid.'
        result['status'] = FAIL
        return result

    # Retrieve the configuration object
    configuration = g.user.get_api().get_configuration(config.default_configuration)

    # Since unallocated address does not exist as an object, first verify if
    # this is an address in a network
    try:
        configuration.get_ip_range_by_ip('IP4Network', ip4_address)
    except PortalException:
        result['message'] = 'IP address is not in a network'
        result['status'] = FAIL
        return result

    # Second, return  Retrieve the IP4 address object and if not found, create one with UNALLOCATED state
    try:
        ip4_address = configuration.get_ip4_address(ip4_address)
    except PortalException as e:
        if 'IP4 address not found' in safe_str(e):
            result['status'] = SUCCESS
            result['data'] = {'state': 'UNALLOCATED', 'mac_address': None, 'name': None}
            return result
        raise e

    # Retrieve the IP4 object name and MAC address properties
    state = ip4_address.get_property('state')

    result['status'] = SUCCESS
    result['data'] = {
        'state': state,
        'mac_address': ip4_address.get_property('macAddress'),
        'name': ip4_address.get_name()
    }

    return result
