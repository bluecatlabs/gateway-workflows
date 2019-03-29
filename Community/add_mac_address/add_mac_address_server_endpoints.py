from flask import g, request, jsonify

from main_app import app
from bluecat import route
from bluecat.util import rest_exception_catcher
from bluecat.util import rest_workflow_permission_required
from bluecat.api_exception import PortalException
from bluecat.server_endpoints import empty_decorator, get_result_template

SUCCESS = 'SUCCESS'
FAIL = 'FAIL'


def get_mac_pools_endpoint(workflow_name, element_id, permissions, result_decorator=None):
    """
    Generate an endpoint for retrieving MACPools. Accepts the following keys in the posted form:
    configuration, view, zone.

    Where:
        configuration - The ID of the configuration containing the MACPools.
    Returns:
        A list of zone paths for autocomplete field and a list of zone paths and zone id's for select field

    :param workflow_name: The name of the workflow that is using this endpoint.
    :param element_id: The ID of the form field using this endpoint.
    :param permissions: What workflow permissions the user needs to access this endpoint.
    :param result_decorator: Function to add custom manipulations to a result set.
    :return: The generated endpoint unique to get_zones_endpoint.
    """
    endpoint = 'get_mac_pools'
    function_endpoint = '%sget_mac_pools' % workflow_name
    view_function = app.view_functions.get(function_endpoint)
    if view_function is not None:
        return endpoint

    if not result_decorator:
        result_decorator = empty_decorator

    @route(app, '/%s/%s' % (workflow_name, endpoint), methods=['POST'])
    @rest_workflow_permission_required(permissions)
    @rest_exception_catcher
    # pylint: disable=unused-variable
    def get_mac_pools():
        """
        Exposed endpoint for retrieving MACPools from a parent configuration. Used for populating simpleautocomplete
        """
        configuration = request.form['configuration']
        return jsonify(result_decorator(get_mac_pools_data(configuration)))
    return endpoint


def get_mac_pools_data(configuration):
    """
    Get a list of MACPools that coressponds to a parent configuration=

    :return: MACPools using result template format.
    """
    # Declare variables
    result = get_result_template()
    result['data']['autocomplete_field'] = []

    # Retrieve the configuration
    try:
        configuration = g.user.get_api().get_entity_by_id(configuration)
    except PortalException as e:
        result['status'] = FAIL
        g.user.logger.warning('%s' % e, msg_type=g.user.logger.EXCEPTION)
        return result

    # Iterate through child MACPool objects of the configuration and append to result
    for mac_pool in configuration.get_children_of_type('MACPool'):
        result['data']['autocomplete_field'].append(mac_pool.get_name())

    result['status'] = SUCCESS
    return result
