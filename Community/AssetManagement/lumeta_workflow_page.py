# Copyright 2019 BlueCat Networks. All rights reserved.

import ipaddress
from flask import request, g, abort, jsonify
from bluecat.api_exception import PortalException, APIException
from bluecat import route, util
from main_app import app

# application config

# Define global variable to hold handle to API object
api = None

#
# GET, PUT or POST
#
@route(app, '/lumeta/getnetworklist', methods=['GET', 'PUT', 'POST'])
@util.rest_workflow_permission_required('lumeta_workflow_page')
@util.rest_exception_catcher
def get_networks_get_networks_page():
    # are we authenticated?
    g.user.logger.info('SUCCESS')
    configurations = None
    configurations_json = []
    if g.user:
        configurations = g.user.get_api().get_configurations()
        for c in configurations:
            print (c)
            configuration_json = {"id": c.get_id(), "name": c.get_name()}
            configurations_json.append(configuration_json)
        return jsonify(configurations_json)


@route(app, '/lumeta/getiplist', methods=['GET', 'PUT', 'POST'])
@util.rest_workflow_permission_required('lumeta_workflow_page')
@util.rest_exception_catcher
def getiplist_getiplist_page():
    # are we authenticated?
    g.user.logger.info('SUCCESS')
    networks = []

    # Return object that contains all the networks (and eventually all ip addresses)
    # list of all properties objects
    ip_addresses = []
    # If name is given, use get_configuration(name)
    if g.user:
        configurations = g.user.get_api().get_configurations()
        for c in configurations:
            print(c)
            configuration_json = {"id": c.get_id(), "name": c.get_name()}

            # FIXME - need code to get network list from configuration id. Is there a call to get children_of_types
            #  (['IP4Block', 'IP4Network', 'IP6Block', 'IP6Network'
            # use get_by_object_types(*,  ['IP4Block', 'IP4Network', 'IP6Block', 'IP6Network']) - returns flat list
            # We might want to request IP4Network, IP6Network
            # FIXME - extract below code in a function and call it for IP4Block and IP6Block
            try:
                for nw in c.get_children_of_type('IP4Block'):
                    print(nw)
                    # get all blocks and networks for block
                    for n in g.user.get_api().get_by_object_types(nw.get_property('CIDR'),
                                                                  ['IP4Network', 'IP4Block', 'IP6Network', 'IP6Block']):
                        if '6' in n.get_type():
                            networks.append({'network_id': n.get_id(), 'display_text': n.get_properties()['prefix']})
                            ip_addresses.extend(calculate_block_stats(n, c.get_id(), c.get_name()))
                        else:
                            networks.append({'network_id': n.get_id(), 'display_text': n.get_properties()['CIDR']})
                            ip_addresses.extend(calculate_block_stats(n, c.get_id(), c.get_name()))

            except Exception as e:
                app.loggererror('get_subnets: ' + e.message)
    return jsonify(ip_addresses)


def calculate_network_stats(bam_network, config_id, config_name):
    if bam_network.get_type() == 'IP4Network':
        network_address = bam_network.get_property('CIDR')
        network = ipaddress.ip_network(network_address)
    else:
        network_address = bam_network.get_property('prefix')
        network = ipaddress.ip_network(network_address)

    ip_addresses = []
    ip_data = {}

    if bam_network.get_type() == 'IP4Network':

        # run below for IP4Address, IP6Address - properties will be populated as well
        for n in bam_network.get_children_of_type('IP4Address'):
            # Sometimes below list contains all ip addresses and sometimes only one for gateway address
            # Look through n.get_properties() and add them to ip_data
            ip_data = {}
            ip_data.update({'ip_address': n.get_address()})
            ip_data.update({'properties': n.get_properties()})
            ip_data.update({'config_id': config_id})
            ip_data.update({'config_name': config_name})
            ip_data.update({'id': n.get_id()})
            ip_addresses.append(ip_data)

        next_address = bam_network.get_next_available_ip4_address()

    else:
        for n in bam_network.get_children_of_type('IP6Address'):
            ip_data = {}
            ip_data.update({'ip_address': n.get_address()})
            ip_data.update({'properties': n.get_properties()})
            ip_data.update({'config_id': config_id})
            ip_data.update({'config_name': config_name})
            ip_data.update({'id': n.get_id()})
            ip_addresses.append(ip_data)

    #return network_data
    return ip_addresses


def calculate_block_stats(bam_block, config_id, config_name):
    if bam_block.get_type() == 'IP6Block':
        block_address = bam_block.get_property('prefix')
        block = ipaddress.ip_network(block_address)
    else:
        block_address = bam_block.get_property('CIDR')
        # block = ipaddress.ip_network(block_address, config_id, config_name)
        block = ipaddress.ip_network(block_address)
    block_data = {}
    block_data_list = []

    if bam_block.get_type() == 'IP4Block':
        for network in bam_block.get_ip4_networks():
            return_data = calculate_network_stats(network, config_id, config_name)
            # This constructs adding network as key with all values that were returned from calculate network stats
            block_data_list.extend(return_data)

        for found_block in bam_block.get_ip4_blocks():
            return_data = calculate_block_stats(found_block, config_id, config_name)
            block_data_list.extend(return_data)

        next_address = bam_block.get_next_available_ip4_address()
        if next_address != '':
            block_data.update({'next_available_address': next_address})
        try:
            next_available = bam_block.get_next_available_ip4_network(256, auto_create=False)
            block_data.update({'next_available_network': next_available})
        except APIException as e:
            # Nothing to do here since we aren't adding anything to the object
            next_available = ''
    elif bam_block.get_type() == 'IP6Block':
        for network in bam_block.get_ip6_networks():
            return_data = calculate_network_stats(network, config_id, config_name)

        for found_block in bam_block.get_ip6_blocks():
            return_data = calculate_block_stats(found_block, config_id, config_name)

    else:
        next_available = ''

    return block_data_list

# to tag address, add_ip4 - get back IP4Address object. Call object.link_entity(entity id of the tag)
#
# GET, PUT or POST
@route(app, '/lumeta/addiplist', methods=['GET', 'PUT', 'POST'])
# @util.rest_workflow_permission_required('addiplist_page')
@util.rest_workflow_permission_required('lumeta_workflow_page')
@util.rest_exception_catcher
def addiplist_addiplist_page():

    # are we authenticated?
    g.user.logger.info('SUCCESS')
    rdata_arr = request.get_json()
    stats = {}
    global api

    for rdata in rdata_arr:
        config_name = rdata["config_name"]
        add_network = rdata["add_network_block"]
        device_list = rdata["deviceList"]
        added_ips = 0
        dup_ips = 0
        # Get API object up front and use it going forward. That way, auth key doesn't expire on us
        # when we are midway in processing
        api = g.user.get_api()
        print(add_network)
        print(device_list)
        config = api.get_configuration(config_name)
        for device in device_list:
            print(device["ip"])
            (added_ip, dup_ip, ip) = add_device(device, config, add_network)
            added_ips += added_ip
            dup_ips += dup_ip

            # Add tag if ip was added
            if added_ip == 1:
                add_tag(ip)
        stats.update({config_name: {"added_ips": added_ips, "dup_ips": dup_ips}})
    return jsonify(stats)


def add_device(device, config, add_network):
    # Algorithm to add ip to BAM
    # check if block exists for this ip address.
    try:
        ip = device["ip"]
        mac = ''
        mac = device["mac"]
        family = device["family"]
        blk_data = None
        dup_ip = 0
        added_ip = 0
        ip_obj = None

        if family == '4':
            blk_data = config.get_ip_range_by_ip('IP4Block', ip)
        else:
            blk_data = config.get_ip_range_by_ip('IP6Block', ip)
        # if block exists, check for network
        network_data = None

        if family == '4':
            network_data = config.get_ip_range_by_ip('IP4Network', ip)
        else:
            network_data = config.get_ip_range_by_ip('IP6Network', ip)

        # If Block and Network exists, add ip address
        # currently, assigning ip address is throwing API exception:Server raised fault: "Duplicate of another item"
        # Need to see how we can catch it
        if blk_data is not None and network_data is not None:
            # Add ip address
            ip_obj = assign_ip(network_data, ip, mac, family)
            added_ip += 1

    # If no  block exists and add_network is set to true, create Block with /32, create Network with /32 and then
    # create ip with /32
    except PortalException as e:
        # No block address containing input ip address exists. Check the flag and create one
        if add_network:
            try:
                # Add Block, then network and finally add ip
                # Below line is returning BAMException - IPv4 Blocks cannot be in size of /31 and /32
                # So, at this point, if there is no container, do not add ip address
                # config.add_ip4_block_by_cidr(ip)
                if blk_data is None:
                    # add /30 for addressblock
                    block_network = ipaddress.ip_network(ip + '/30', strict=False)
                    config.add_ip4_block_by_cidr(block_network.exploded)
                    blk_data = config.get_ip_range_by_ip('IP4Block', ip)

                if blk_data is not None:
                    # create network  in block
                    blk_data.add_ip4_network(ip + '/32')

                    # create ip under above created network
                    network_data = config.get_ip_range_by_ip('IP4Network', ip)
                    if network_data is not None:
                        # Add ip address
                        ip_obj = assign_ip(network_data, ip, mac, family)
                        added_ip += 1
            except APIException as ex:
                if "Duplicate" in ex.get_message():
                    dup_ip += 1
                # else:
                # Seeing intermittent error while adding address block, so had to stop logging error
                # app.loggererror('add_ip: ' + ex.message)
    except APIException as ex:
        # when ip address already exists, it returns BAMException with message 'Server raised fault: "Duplicate of another item"'
        # "Duplicate" in ex.get_message()
        if "Duplicate" in ex.get_message():
            dup_ip += 1
        else:
            # TODO - how to log info message and not error?
            app.loggererror('add_ip: ' + ex.get_message())
    return (added_ip, dup_ip, ip_obj)


def assign_ip(network_data, ip, mac, family):
    if mac is not '':
        if family == '4':
            ip = network_data.assign_ip4_address(ip, mac, '', 'MAKE_DHCP_RESERVED')
        else:
            ip = network_data.assign_ip6_address(ip, mac, '', 'MAKE_DHCP_RESERVED')
    else:
        if family == '4':
            ip = network_data.assign_ip4_address(ip, '', '', 'MAKE_STATIC')
        else:
            ip = network_data.assign_ip6_address(ip, '', '', 'MAKE_STATIC')
    return ip


def add_tag(ip):
    tag_group = None
    tag = None
    try:
        tag_group = api.get_tag_group_by_name("Lumeta")

        # If tag group exists, chances are that tag exists as well, but just in case if it doesn't
        tag = tag_group.get_tag_by_name("Discovered Device")

    except PortalException as e:
        if tag_group is None:
            # Tag group does not exist, create one
            tag_group = api.add_tag_group("Lumeta")
        if tag is None:
            # Get tag group object. above API to add tag group is only returning object id instead of entire object
            # Calling add_tag on it is throwing exception 'int' object has no attribute 'add_tag'
            tag_group = api.get_tag_group_by_name("Lumeta")
            # Create Tag under Lumeta
            tag = tag_group.add_tag("Discovered Device")
    try:
        # assign tag to ip
        ip.link_entity(tag)
    except APIException as ex:
        print(ex.get_message())
