# Copyright 2019 BlueCat Networks. All rights reserved.

from flask import request, g, jsonify

from bluecat import route, util
from main_app import app
from bluecat.api_exception import APIException, BAMException, PortalException
from .manage_dhcp_config import DEFAULT_CONFIG_NAME, DEFAULT_VIEW_NAME, DEFAULT_VIEW_ID


#
# GET, PUT or POST
#
@route(app, '/manage_dhcp/endpoint', methods=['GET', 'PUT', 'POST'])
@util.rest_workflow_permission_required('manage_dhcp')
@util.rest_exception_catcher
def manage_dhcp_endpoint():
    # are we authenticated?
    g.user.logger.info('SUCCESS')
    return jsonify({"message": 'The manage_dhcp service is running'}), 200


@route(app, '/manage_dhcp/create_reservation', methods=['POST'])
@util.rest_workflow_permission_required('manage_dhcp')
@util.rest_exception_catcher
def create_reservation_endpoint():
    json_data = request.get_json()
    response_data = {'message': ''}
    response_code = 200
    response_message = ''

    if 'mac' not in json_data or json_data['mac'] == '':
        response_code = 400
        response_message = 'mac not provided'
    elif 'ip' not in json_data or json_data['ip'] == '':
        response_code = 400
        response_message = 'ip not provided'
    elif ':' in json_data['ip'].strip() and ('duid' not in json_data or json_data['duid'] == ''):
        response_code = 400
        response_message = 'IPv6 Address detected, duid not provided'

    if response_code == 200:
        try:
            configuration = g.user.get_api().get_configuration(DEFAULT_CONFIG_NAME)
            if ':' in json_data['ip'].strip():
                new_address = configuration.assign_ip6_address('MAKE_DHCP_RESERVED', json_data['ip'].strip(),
                                                               mac_address=json_data['mac'], duid=json_data['duid'])
            else:
                new_address = configuration.assign_ip4_address(json_data['ip'].strip(), json_data['mac'],
                                                               '', 'MAKE_DHCP_RESERVED')

            response_data['ip_id'] = new_address.get_id()
            response_message = 'Successfully reserved IP address: %s' % new_address.get_address()

        except (APIException, BAMException, PortalException) as e:
            response_code = 500
            response_message = 'Unable to create the reservation %s with mac %s, exception: %s' %\
                               (json_data['ip'].strip(), json_data['mac'].strip(), util.safe_str(e))

    g.user.logger.info(
        'create_reservation returned with the following message: %s' % response_message)
    response_data['message'] = response_message
    return jsonify(response_data), response_code


@route(app, '/manage_dhcp/delete_reservation', methods=['POST'])
@util.rest_workflow_permission_required('manage_dhcp')
@util.rest_exception_catcher
def delete_reservation_endpoint():
    json_data = request.get_json()
    response_data = {'message': ''}
    response_code = 200
    response_message = ''

    if 'ip' not in json_data or json_data['ip'] == '':
        response_code = 400
        response_message = 'ip not provided'

    if response_code == 200:
        try:
            configuration = g.user.get_api().get_configuration(DEFAULT_CONFIG_NAME)
            if ':' in json_data['ip'].strip():
                address = configuration.get_ip6_address(json_data['ip'].strip())
            else:
                address = configuration.get_ip4_address(json_data['ip'].strip())

            address.delete()
            response_message = 'Successfully deleted the reservation for IP address: %s' % json_data['ip'].strip()

        except (APIException, BAMException, PortalException) as e:
            response_code = 500
            response_message = 'Unable to delete the reservation %s, exception: %s' % \
                               (json_data['record_name'].strip(), util.safe_str(e))

    g.user.logger.info(
        'delete_reservation returned with the following message: %s' % response_message)
    response_data['message'] = response_message
    return jsonify(response_data), response_code


@route(app, '/manage_dhcp/create_scope', methods=['POST'])
@util.rest_workflow_permission_required('manage_dhcp')
@util.rest_exception_catcher
def create_scope_endpoint():
    json_data = request.get_json()
    response_data = {'message': ''}
    response_code = 200

    if 'network' not in json_data or json_data['network'] == '':
        response_code = 400
        response_message = 'network not provided'
    elif ':' in json_data['network'].strip():
        if 'size' not in json_data or json_data['size'] == '':
            response_code = 400
            response_message = 'IPv6 Network detected, size not provided'
    else:
        if 'start' not in json_data or json_data['start'] == '':
            response_code = 400
            response_message = 'IPv4 Network detected, ip not provided'
        elif 'end' not in json_data or json_data['end'] == '':
            response_code = 400
            response_message = 'IPv4 Network detected, ip not provided'
        # elif int(json_data['end'].strip()) > int(json_data['start'].strip()):
        #     response_code = 400
        #     response_message = 'IPv4 Network detected, end of requested range is not greater than the start'

    if response_code == 200:
        try:
            networks = g.user.get_api().get_by_object_types(json_data['network'].strip(), ['IP6Network', 'IP4Network'])
            found_network = None
            for network in networks:
                if network.get_type() == 'IP6Network' and network.get_property('prefix') == json_data['network'].strip():
                    range_id = g.user.get_api()._api_client.service.addDHCP6RangeBySize(network.get_id(), '', json_data['size'].strip(), 'defineRangeBy=AUTOCREATE_BY_SIZE')
                    found_network = network
                    break
                elif network.get_property('CIDR') == json_data['network'].strip():
                    found_network = network
                    split = network.get_property('CIDR').split('.')
                    prefix = split[0] + '.' + split[1] + '.' + split[2] + '.'
                    range_id = network.add_dhcp4_range(prefix + json_data['start'].strip(), prefix + json_data['end'].strip())
                    break

            if found_network:
                response_message = 'Successfully created the scope for network %s with ID %s' % (json_data['network'].strip(), range_id)
            else:
                response_message = 'No matching network found: %s' % json_data['network'].strip()

        except (APIException, BAMException, PortalException) as e:
            response_code = 500
            response_message = 'Unable to create the scope on network %s, exception: %s' %\
                               (json_data['network'].strip(), util.safe_str(e))

    g.user.logger.info(
        'create_scope returned with the following message: %s' % response_message)
    response_data['message'] = response_message
    return jsonify(response_data), response_code


@route(app, '/manage_dhcp/delete_scope', methods=['POST'])
@util.rest_workflow_permission_required('manage_dhcp')
@util.rest_exception_catcher
def delete_scope_endpoint():
    json_data = request.get_json()
    response_data = {'message': ''}
    response_code = 200
    response_message = ''

    if 'id' not in json_data or json_data['id'] == '':
        response_code = 400
        response_message = 'id not provided'

    if response_code == 200:
        try:
            scope = g.user.get_api().get_entity_by_id(json_data['id'].strip())

            scope.delete()

            response_message = 'Successfully deleted the scope with ID: %s' % json_data['id'].strip()

        except (APIException, BAMException, PortalException) as e:
            response_code = 500
            response_message = 'Unable to delete the scope %s, exception: %s' % \
                               (json_data['record_name'].strip(), util.safe_str(e))

    g.user.logger.info(
        'delete_scope returned with the following message: %s' % response_message)
    response_data['message'] = response_message
    return jsonify(response_data), response_code


@route(app, '/manage_dhcp/add_option', methods=['POST'])
@util.rest_workflow_permission_required('manage_dhcp')
@util.rest_exception_catcher
def add_option_endpoint():
    json_data = request.get_json()
    response_data = {'message': ''}
    response_code = 200

    if 'network' not in json_data or json_data['network'] == '':
        response_code = 400
        response_message = 'network not provided'
    elif 'option_value' not in json_data or json_data['option_value'] == '':
        response_code = 400
        response_message = 'option_value ip not provided'

    if response_code == 200:
        try:
            networks = g.user.get_api().get_by_object_types(json_data['network'].strip(), ['IP6Network', 'IP4Network'])
            found_network = None
            for network in networks:
                if network.get_type() == 'IP6Network' and network.get_property('prefix') == json_data['network'].strip():
                    found_network = network
                    option_id = g.user.get_api()._api_client.service.addDHCP6ClientDeploymentOption(
                        found_network.get_id(), 'tftp-server', json_data['option_value'].strip(), '')
                    break
                elif network.get_property('CIDR') == json_data['network'].strip():
                    found_network = network
                    option_id = g.user.get_api()._api_client.service.addDHCPClientDeploymentOption(
                        found_network.get_id(), 'tftp-server', json_data['option_value'].strip(), '')
                    break

            if found_network:
                response_message = 'Successfully added the option to network %s with ID %s' % (json_data['network'].strip(), found_network.get_id())
            else:
                response_message = 'No matching network found: %s' % json_data['network'].strip()

        except (APIException, BAMException, PortalException) as e:
            response_code = 500
            response_message = 'Unable to add the option to the network network %s, exception: %s' %\
                               (json_data['network'].strip(), util.safe_str(e))

    g.user.logger.info(
        'add_option returned with the following message: %s' % response_message)
    response_data['message'] = response_message
    return jsonify(response_data), response_code


@route(app, '/manage_dhcp/reserve_next_available', methods=['POST'])
@util.rest_workflow_permission_required('manage_dhcp')
@util.rest_exception_catcher
def reserve_next_available_endpoint():
    json_data = request.get_json()
    response_data = {'message': ''}
    response_code = 200

    if 'network' not in json_data or json_data['network'] == '':
        response_code = 400
        response_message = 'network not provided'
    if 'host_name' not in json_data or json_data['host_name'] == '':
        response_code = 400
        response_message = 'host_name not provided'
    if 'zone' not in json_data or json_data['zone'] == '':
        response_code = 400
        response_message = 'zone not provided'
    if 'mac_address' not in json_data or json_data['mac_address'] == '':
        response_code = 400
        response_message = 'mac_address not provided'

    if response_code == 200:
        try:
            networks = g.user.get_api().get_by_object_types(json_data['network'].strip(), 'IP4Network')
            found_network = None
            for network in networks:
                if network.get_property('CIDR') == json_data['network'].strip():
                    found_network = network
                    host_string = '%s.%s,%s,true,false' % (json_data['host_name'].strip(), json_data['zone'].strip(), DEFAULT_VIEW_ID)
                    new_address = found_network.assign_next_available_ip4_address(json_data['mac_address'].strip(), host_string, 'MAKE_DHCP_RESERVED')
                    break

            if found_network:
                response_message = 'Successfully created the host %s.%s to the network with IP address %s' % (json_data['host_name'].strip(), json_data['zone'].strip(), new_address.get_address())
                response_data['ip'] = new_address.get_address()
                response_data['ip_id'] = new_address.get_id()
            else:
                response_message = 'No matching network found: %s' % json_data['network'].strip()

        except (APIException, BAMException, PortalException) as e:
            response_code = 500
            response_message = 'Unable to add the option to the network network %s, exception: %s' %\
                               (json_data['network'].strip(), util.safe_str(e))

    g.user.logger.info(
        'reserve_next_available returned with the following message: %s' % response_message)
    response_data['message'] = response_message
    return jsonify(response_data), response_code
