
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
            {"title": "IP Address"},
            {'title': 'State'},
            {'title': 'Absolute Name'},
            {'title': 'Host Name'},
            {'title': 'PTR Record'},
        ],
        "data": [

        ]
    }

def raw_entities_to_table_data(records):
    # pylint: disable=redefined-outer-name
    data = {'columns': [{'title': 'IP Address'},
                        {'title': 'State'},
                        {'title': 'Absolute Name'},
                        {'title': 'Host Name'},
                        {'title': 'PTR Record'},],
            'data': []}

    # Iterate through each record
    for record in records:
        ipinfo = record[0]
        address = ipinfo.get_property('address')
        addstate = ipinfo.get_property('state')

        dnsinfo = record[1]
        for dns in dnsinfo:
            absname = dns.get_property('absoluteName')
            dnsname = dns.name
            reverse = dns.get_property('reverseRecord')
            data['data'].append([address , addstate , absname , dnsname , reverse])
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
            ip4_network = request.form['ip4_network']
            configuration = g.user.get_api().get_configuration(config.default_configuration)
            networks = configuration.get_ip4_networks_by_hint(ip4_network.split('/', 1)[0])
            net_id = networks[0].get_id()
            network = g.user.get_api().get_entity_by_id(net_id)
            ip4_addresses = g.user.get_api()._api_client.service.getEntities(network.get_id(), 'IP4Address', 0, 100)

            new_ip4_address = []
            for ip4_address in ip4_addresses.item:
                ip4_address = g.user.get_api().instantiate_entity(ip4_address)
                new_ip4_address.append(ip4_address)

            print("Found {} IP Addresses with Network {}".format(len(new_ip4_address), network.get_property('CIDR')))

            # Calling the new API
            records = configuration.get_host_records_by_ip(new_ip4_address)

            # Parse response object into table data
            data = raw_entities_to_table_data(records)

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

def find_objects_for_report(result_decorator=None):
    """Retrieve a list of properties for the table"""
    # pylint: disable=broad-except
    try:
        ip4_network = request.form['ip4_network']
        configuration = g.user.get_api().get_configuration(config.default_configuration)
        networks = configuration.get_ip4_networks_by_hint(ip4_network.split('/', 1)[0])
        net_id = networks[0].get_id()
        network = g.user.get_api().get_entity_by_id(net_id)
        ip4_addresses = g.user.get_api()._api_client.service.getEntities(network.get_id(), 'IP4Address', 0, 100)

        new_ip4_address = []
        for ip4_address in ip4_addresses.item:
            ip4_address = g.user.get_api().instantiate_entity(ip4_address)
            new_ip4_address.append(ip4_address)

        print("Found {} IP Addresses with Network {}".format(len(new_ip4_address), network.get_property('CIDR')))

        # Calling the new API
        records = configuration.get_host_records_by_ip(new_ip4_address)

        data = []

        for record in records:
            ipinfo = record[0]
            address = ipinfo.get_property('address')
            addstate = ipinfo.get_property('state')

            dnsinfo = record[1]
            for dns in dnsinfo:
                absname = dns.get_property('absoluteName')
                dnsname = dns.name
                reverse = dns.get_property('reverseRecord')
                data.append([address, addstate, absname, dnsname, reverse])

        return data

        # If no entities were found return with failure state and message
        if len(data) == 0:
            data['status'] = 'FAIL'
            data['message'] = 'No records  were found.'
        else:
            data['status'] = 'SUCCESS'
        return data

    except Exception as e:
        data['status'] = 'FAIL'
        data['message'] = str(e)
        return data