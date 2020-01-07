# Copyright 2020 BlueCat Networks. All rights reserved.
import json
import bluecat_portal.config as config

from flask import request, g, abort, jsonify
from bluecat import route, util
from main_app import app
from ..vro_configuration import vro_config


@route(app, '/vro_provision_server/vro_provision_server_endpoint', methods=['POST'])
@util.rest_workflow_permission_required('vro_provision_server_page')
@util.rest_exception_catcher
def vro_provision_server_vro_provision_server_page():
    data = json.loads(request.data)

    configuration = g.user.get_api().get_configuration(vro_config.default_configuration)
    view = configuration.get_view(vro_config.default_view)

    vro_tag = g.user.get_api().get_tag_group_by_name('vRO Configuration')
    network_tag = vro_tag.get_child_by_name('vRO Networks', 'Tag')
    networks = network_tag.get_linked_entities('IP4Network')

    # Building the host properties string used to create the host
    props = {'excludeDHCPRange': 'True'}

    for network in networks:
        try:
            hostinfo = util.safe_str(data['hostname']) + '.' + vro_config.default_zone + ',' + util.safe_str(
                view.get_id()) + ',' + vro_config.default_reverse_flag + ',' + 'False'

            assigned_ip = network.assign_next_available_ip4_address(data['mac'], hostinfo, 'MAKE_DHCP_RESERVED', properties =props)
            break
        except Exception as e:
            if 'used by another ip' in util.safe_str(e).lower():
                raise e
            else:
                g.user.logger.warning('All IPs are used in Network, Getting the next Network in vRO Networks Tag!')
                continue
        else:
            if 'network' not in globals():
                raise Exception('All networks are full')

    result = assigned_ip.to_json()
    result['hostname'] = data['hostname'] + '.' + vro_config.default_zone
    # Log out
    g.user.logout()

    return jsonify(result)
