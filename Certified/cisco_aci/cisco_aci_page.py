# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By: BlueCat Networks
# Date: 2020-11-26
# Gateway Version: 20.3.1
# Description: Certified Gateway workflow
"""
Cisco ACI page
"""
import os

from acitoolkit.acisession import CredentialsError
import acitoolkit.acitoolkit as ACI
import queue
from flask import render_template, g, jsonify, request, flash

from bluecat import route, util
from bluecat.util import has_response
from bluecat.server_endpoints import get_result_template, SUCCESS, empty_decorator, FAIL
from bluecat.api_exception import BAMException, PortalException
from bluecat.internal.wrappers.rest_fault import RESTFault
import config.default_config as config
from main_app import app
from .cisco_aci_form import GenericFormTemplate, raw_table_data
import ipaddress
import requests.exceptions


# Globals

progress = None
messages = queue.Queue()


def get_api():
    """
    Fetches API from flask globals
    :return: API
    """
    return g.user.get_api()


# pylint: disable=protected-access,too-many-locals
def create_aci_fabric(aci_session, configuration):
    """Creates corresponding ACI Fabric Devices in BAM."""
    nodes = aci_session.get('/api/node/class/fabricNode.json')
    if nodes.ok:
        nodes = nodes.json()['imdata']
    else:
        app.logger.error(nodes.text)
        nodes = []

    top_system = aci_session.get('/api/node/class/topSystem.json')
    if top_system.ok:
        top_system = top_system.json()['imdata']
    else:
        app.logger.error(top_system.text)
        top_system = []

    infrastructure_type = get_or_create_device_type(0, "Cisco ACI Infrastructure", 'DeviceType')
    apic_subtype = get_or_create_device_type(infrastructure_type.get_id(), "Cisco ACI APIC", 'DeviceSubtype')
    spine_subtype = get_or_create_device_type(infrastructure_type.get_id(), "Cisco ACI SPINE", 'DeviceSubtype')
    leaf_subtype = get_or_create_device_type(infrastructure_type.get_id(), "Cisco ACI LEAF", 'DeviceSubtype')

    id_to_address_map = {}
    for system in top_system:
        id_to_address_map[system['topSystem']['attributes']['id']] = system['topSystem']['attributes']['address']

    for node in nodes:
        vendor = node['fabricNode']['attributes']['vendor']
        model = node['fabricNode']['attributes']['model']
        serial = node['fabricNode']['attributes']['serial']
        name = node['fabricNode']['attributes']['name']
        role = node['fabricNode']['attributes']['role']
        dn = node['fabricNode']['attributes']['dn']
        state = node['fabricNode']['attributes']['fabricSt']
        nodeid = node['fabricNode']['attributes']['id']
        address = None
        if nodeid in id_to_address_map:
            address = id_to_address_map[nodeid]

        properties = ""
        properties = properties + "dn=" + dn
        properties = properties + "|vendor=" + vendor
        properties = properties + "|model=" + model
        properties = properties + "|serial=" + serial
        properties = properties + "|state=" + state

        subtype_id = None
        if role == "controller":
            subtype_id = apic_subtype.get_id()
        elif role == "spine":
            subtype_id = spine_subtype.get_id()
        elif role == "leaf":
            subtype_id = leaf_subtype.get_id()

        addressv6 = ""
        controller_device = get_device(configuration.get_id(), name)

        if controller_device is not None:
            get_api()._api_client.service.delete(controller_device.get_id())
        if address is not None and subtype_id is not None:
            try:
                add_device(
                    configuration.get_id(),
                    name,
                    infrastructure_type.get_id(),
                    subtype_id,
                    address,
                    addressv6,
                    properties,
                )
            except BAMException as e:
                g.user.logger.info(str(e))
            else:
                message = 'Added ACI Fabric {role}: "{name}" with Bridge Domain: "{bd}",' \
                          ' Serial: "{serial}", Model: "{model}", State: "{state}", IPv4 Address: "{address}",' \
                          ' and IPv6 Address: "{addressv6}" to BAM Configuration: "{config}"'

                g.user.logger.info(
                    message.format(
                        role=role.capitalize(),
                        name=name,
                        bd=dn,
                        serial=serial,
                        model=model,
                        state=state,
                        address=address,
                        addressv6=addressv6,
                        config=configuration.get_name(),
                    ),
                )


def check_and_create_tenant_udfs():
    """Checks if UDFs required for Cisco ACI are already present in BAM and creates them if they aren't."""
    udf_attributes = {
        'type': 'TEXT',
        'defaultValue': '',
        'validatorProperties': '',
        'required': False,
        'hideFromSearch': False,
        'renderAsRadioButton': False,
    }
    try:
        get_api()._api_client.service.addUserDefinedField(
            'Device',
            dict(udf_attributes, name='app', displayName='App Profile'),
        )
    except RESTFault as e:
        if 'duplicate' not in str(e).lower():
            raise e
    try:
        get_api()._api_client.service.addUserDefinedField(
            'Device',
            dict(udf_attributes, name='dn', displayName='DN'),
        )
    except RESTFault as e:
        if 'duplicate' not in str(e).lower():
            raise e
    try:
        get_api()._api_client.service.addUserDefinedField(
            'Device',
            dict(udf_attributes, name='epg', displayName='EPG'),
        )
    except RESTFault as e:
        if 'duplicate' not in str(e).lower():
            raise e
    try:
        get_api()._api_client.service.addUserDefinedField(
            'IP4Network',
            dict(udf_attributes, name='aciscope', displayName='ACI Scope'),
        )
    except RESTFault as e:
        if 'duplicate' not in str(e).lower():
            raise e


def check_and_create_fabric_udfs():
    """Checks if UDFs required for Cisco ACI are already present in BAM and creates them if they aren't."""
    # Not done, check https://collab.bluecatnetworks.com/display/NEWPM/CISCO+ACI for all the UDFs to be added.
    udf_attributes = {
        'type': 'TEXT',
        'defaultValue': '',
        'validatorProperties': '',
        'required': False,
        'hideFromSearch': False,
        'renderAsRadioButton': False,
    }
    try:
        get_api()._api_client.service.addUserDefinedField(
            'Device',
            dict(udf_attributes, name='dn', displayName='DN'),
        )
    except RESTFault as e:
        if 'duplicate' not in str(e).lower():
            raise e
    try:
        get_api()._api_client.service.addUserDefinedField(
            'Device',
            dict(udf_attributes, name='model', displayName='Model'),
        )
    except RESTFault as e:
        if 'duplicate' not in str(e).lower():
            raise e
    try:
        get_api()._api_client.service.addUserDefinedField(
            'Device',
            dict(udf_attributes, name='serial', displayName='Serial'),
        )
    except RESTFault as e:
        if 'duplicate' not in str(e).lower():
            raise e
    try:
        get_api()._api_client.service.addUserDefinedField(
            'Device',
            dict(udf_attributes, name='state', displayName='State'),
        )
    except RESTFault as e:
        if 'duplicate' not in str(e).lower():
            raise e
    try:
        get_api()._api_client.service.addUserDefinedField(
            'Device',
            dict(udf_attributes, name='vendor', displayName='Vendor'),
        )
    except RESTFault as e:
        if 'duplicate' not in str(e).lower():
            raise e
    try:
        get_api()._api_client.service.addUserDefinedField(
            'Device',
            dict(udf_attributes, name='Port', displayName='Port'),
        )
    except RESTFault as e:
        if 'duplicate' not in str(e).lower():
            raise e


def create_tenant_tags(tenant_name):
    """Creates tags used to categorize tenants in BAM."""
    try:
        tag_group = get_api().get_tag_group_by_name('Cisco ACI Tenants')
    except PortalException:
        tag_group = get_api().get_entity_by_id(get_api().add_tag_group('Cisco ACI Tenants', ''))

    try:
        tag_group.add_tag(tenant_name)
    except BAMException as e:
        if 'duplicate' not in e.get_message().lower():
            raise e


# pylint: disable=protected-access
def get_or_create_device_type(parent_id, name, device_type):
    """Gets device type or creates device type if it doesn't exist."""
    result = get_api()._api_client.service.getEntityByName(parent_id, name, device_type)
    if has_response(result):
        device_type_object = get_api().instantiate_entity(result)
    elif parent_id == 0:
        device_type_object = get_api()._api_client.service.addDeviceType(name, '')
        device_type_object = get_api().get_entity_by_id(device_type_object)
    else:
        device_type_object = get_api()._api_client.service.addDeviceSubtype(parent_id, name, '')
        device_type_object = get_api().get_entity_by_id(device_type_object)
    return device_type_object


# pylint: disable=protected-access
def add_device(config_id, name, device_type_id, device_subtype_id, ip4address, ip6address, properties):
    """Add device to BAM."""
    response = get_api()._api_client.service.addDevice(config_id, name, device_type_id, device_subtype_id, ip4address,
                                                       ip6address, properties)
    return get_api().get_entity_by_id(response)


# pylint: disable=protected-access
def get_device(config_id, device_name):
    """Get device from BAM."""
    device = None
    response = get_api()._api_client.service.getEntityByName(config_id, device_name, "Device")
    if has_response(response):
        device = get_api().instantiate_entity(response)
    return device


def find_teppools(aci_session):
    """Find TEPools in ACI."""
    tep_pools = list()
    pod_policy = aci_session.get('/api/node/class/fabricSetupP.json')
    if pod_policy.ok:
        pod_policy = pod_policy.json()['imdata']
    else:
        app.logger.error(pod_policy.text)
        pod_policy = []
    for pod in pod_policy:
        tep_pools.append(pod['fabricSetupP']['attributes']['tepPool'])
    return tep_pools


def populate_table_data(tenants):
    """Generates entries used to populate tenant table."""
    result = []
    for tenant in tenants:
        name = str(tenant.name)
        checkbox_html_template = '<input type="checkbox" id="{name}" name="{name}" {option} checked>'
        import_option = 'class="table_checkbox" onchange="toggle_import_checkboxes(this, \'{}\', 1)"'.format(name)
        other_option = 'class="table_checkbox" onchange="get_and_toggle_column_header_checkbox({index})"'
        import_name = name + '_import'
        endpoint_devices_name = name + '_import_endpoint_devices'
        overwrite_name = name + '_overwrite'
        result.append([name,
                       checkbox_html_template.format(name=import_name, option=import_option),
                       checkbox_html_template.format(name=endpoint_devices_name, option=other_option.format(index=2)),
                       checkbox_html_template.format(name=overwrite_name, option=other_option.format(index=3)),
                      ])
    return result


def module_path():
    """
    Get module path.

    :return:
    """
    return os.path.dirname(os.path.abspath(__file__))


# Add configurations to BAM and TAGS them
def add_configurations(bam_confs):
    """
    Create configurations in BAM
    :param bam_confs: List of configuration names
    :return:
    """
    global messages
    has_success = True
    for conf in bam_confs:
        try:
            conf_entity = get_api().get_configuration(conf[0])
        except PortalException:
            conf_entity = get_api().create_configuration(conf[0])
        conf_entity.set_property('configurationGroup', conf[1])
        conf_entity.update()

        g.user.logger.info('Added BAM Configuration: "{config}" for ACI Tenant: "{tenant}"'.format(config=conf[0],
                                                                                                   tenant=conf[1]))
        tag_group = get_api().get_tag_group_by_name('Cisco ACI Tenants')
        try:
            tag = tag_group.get_tag_by_name(conf[1])
            g.user.logger.info('Added BAM Tag: "{tag}" for ACI Tenant: "{tenant}"'.format(tag=conf[1],
                                                                                          tenant=conf[1]))
        except PortalException:
            tag = tag_group.add_tag(conf[1])
        try:
            conf_entity.link_entity(tag)
            g.user.logger.info('Linked BAM Configuration: "{config}" with BAM Tag: "{tag}"'.format(config=conf[0],
                                                                                                   tag=conf[1]))
        except BAMException:
            error_message = 'Failed to link BAM Configuration: "{config}" with BAM Tag: "{tag}", link may already exist'
            g.user.logger.info(error_message.format(config=conf[0], tag=conf[1]))

    return has_success


def add_subnets(subs):
    """
    Add subnets to BAM
    :param subs: List of subnets to import
    :return:
    """
    global messages
    has_success = True
    try:
        tag_group = get_api().get_tag_group_by_name('Cisco ACI Tenants')
    except (BAMException, PortalException):
        message = 'Error! Failed when getting Cisco ACI Tenants tag group, skipping subnet sync.'
        messages.put(message)
        has_success = False
        return has_success

    for sub in subs:
        network_gw = sub[3]
        if not network_gw:
            continue
        tenant_name = str(sub[0])
        conf_name = "Cisco ACI: [" + tenant_name + "/" + sub[1] + "/" + sub[2] + "]"
        try:
            conf = get_api().get_configuration(conf_name)
            aci_subnet = ipaddress.IPv4Network(network_gw, strict=False)
            network_as_cidr = str(aci_subnet)
            blk = conf.add_ip4_block_by_cidr(network_as_cidr, properties="name=Cisco ACI Block")
            message = 'Added Subnet Block with CIDR: "{cidr}" to BAM Configuration: "{config}"'
            g.user.logger.info(message.format(cidr=network_as_cidr, config=conf_name))
            tag = tag_group.get_tag_by_name(tenant_name)
            blk.link_entity(tag)
            message = 'Linked Subnet Block with CIDR: "{cidr}" to BAM Tenant Tag: "{tag}"'
            g.user.logger.info(message.format(cidr=network_as_cidr, tag=tenant_name))
            aci_scope = sub[4]
            props = "name=Cisco ACI Network|aciscope=" + aci_scope
            ss = blk.add_ip4_network(network_as_cidr, properties=props)
            message = 'Added ACI Subnet with CIDR: "{cidr}" to BAM Configuration: "{config}"'
            g.user.logger.info(message.format(cidr=network_as_cidr, config=conf_name))
            ss.link_entity(tag)
            message = 'Linked ACI Subnet in BAM with CIDR: "{cidr}" to BAM Tenant Tag: "{tag}"'
            g.user.logger.info(message.format(cidr=network_as_cidr, tag=tenant_name))
        except (PortalException, BAMException) as e:
            g.user.logger.error(e)
            message = 'Error! Failed when adding Subnet with Network Gateway: {gateway} for Tenant: {tenant}.'
            message = message.format(gateway=str(network_gw), tenant=tenant_name)
            g.user.logger.error(message)
            messages.put(message)
            has_success = False
            continue
    return has_success


def get_bridge_domain(aci_subnets, eip):
    """
    function to return a bridge domain name from tenant, app and end device IP
    :param aci_subnets: List of aci subnets
    :param eip: ACO end device IP
    :return: Bridge domain name
    """
    for bd_name, networks in aci_subnets.items():
        for network in networks:
            if ipaddress.ip_address(eip) in ipaddress.IPv4Network(network.addr, strict=False):
                return bd_name

    return None


def add_endpoints(epds):
    """
    Add endpoint information to BAM
    :param epds: List of endpoints
    :return:
    """

    global messages
    has_success = True
    try:
        tag_group = get_api().get_tag_group_by_name('Cisco ACI Tenants')
    except (BAMException, PortalException):
        message = 'Error! Failed when getting Cisco ACI Tenants tag group, skipping endpoint sync.'
        messages.put(message)
        has_success = False
        return has_success

    infrastructure_type = get_or_create_device_type(0, "Cisco ACI Infrastructure", 'DeviceType')
    endpoint_subtype = get_or_create_device_type(infrastructure_type.get_id(), "End Point Device", 'DeviceSubtype')

    for ep in epds:
        address = ep[2]
        addressv6 = ""
        tenant_name = ep[0]
        mac = ep[1]
        conf_name = ep[6]
        try:
            conf = get_api().get_configuration(conf_name)
            properties = "dn=" + ep[3] + "|app=" + ep[4] + "|epg=" + ep[5]
            if address != "0.0.0.0":
                device = add_device(conf.get_id(), mac, infrastructure_type.get_id(), endpoint_subtype.get_id(),
                                    address, addressv6, properties)
                message = 'Added ACI Endpoint Device with MAC Address: "{mac}", Bridge Domain: "{bd}",' \
                          ' App: "{app}", IPv4 Address: "{address}", and IPv6 Address: "{addressv6}" to' \
                          ' BAM Configuration: "{config}"'
                g.user.logger.info(message.format(name=ep[5], mac=mac, bd=ep[3], app=ep[4], address=address,
                                                  addressv6=addressv6, config=conf_name))
                tag = tag_group.get_tag_by_name(tenant_name)
                device.link_entity(tag)
                message = 'Linked ACI Endpoint: "{name}" to BAM Tenant Tag: "{tag}"'
                g.user.logger.info(message.format(name=ep[5], tag=tenant_name))
        except (BAMException, PortalException) as e:
            g.user.logger.error(e)
            message = 'Error! Failed creating device for endpoint with MAC Address: {mac} and IP: {ip} for Tenant:' \
                      ' {tenant}. Please check the Gateway server logs for more details.'
            messages.put(message.format(mac=mac, ip=address, tenant=tenant_name))
            has_success = False
            continue
    return has_success


def purge_tenant(tenant_name):
    """
    Delete tenants from BAM
    :param tenant_name: Tenant Name
    :return:
    """

    purge_list = set()
    configurations = get_api().get_configurations()
    tenant_prefix = "Cisco ACI: [" + tenant_name

    for configuration in configurations:
        if configuration.get_name().startswith(tenant_prefix):
            purge_list.add(configuration.get_id())

    for conf_id in purge_list:
        get_api().delete_configuration(entity_id=conf_id)


def fetch_tenant_info(aci_session, tenant, fetch_endpoints=False):
    """

    :param aci_session: ACI session
    :param tenant: Cisco Tenant Instance
    :param fetch_endpoints: Boolean - Import Endpoints
    :return: subnets, configurations and endpoints information
    """
    aci_subnets = list()
    bam_confs = list()
    endpoint_data = list()

    apps = list(ACI.AppProfile.get(aci_session, tenant))
    bds = list(ACI.BridgeDomain.get(aci_session, tenant))
    subnets = dict()

    for bd in bds:
        subnets[bd.name] = ACI.Subnet.get(aci_session, bd, tenant)

    for appp in apps:
        for bd in bds:
            conf = "Cisco ACI: [" + tenant.name + "/" + appp.name + "/" + bd.name + "]"
            bam_confs.append((conf, tenant.name))
            if len(subnets[bd.name]) == 0:
                aci_subnets.append((tenant.name, appp.name, bd.name, "", ""))
            else:
                for subnet in subnets[bd.name]:
                    aci_subnets.append((tenant.name, appp.name, bd.name, subnet.addr, subnet.get_scope()))
        if fetch_endpoints:
            epgs = ACI.EPG.get(aci_session, parent=appp, tenant=tenant)
            for epg in epgs:
                endpoints = ACI.Endpoint.get_all_by_epg(aci_session, tenant.name, appp.name, epg.name,
                                                        with_interface_attachments=False)
                for ep in endpoints:
                    if ipaddress.ip_address(ep.ip).version == 4 and (ep.ip != "0.0.0.0"):
                        bd_name = get_bridge_domain(subnets, ep.ip)
                        if bd_name:
                            epbamconf = "Cisco ACI: [" + tenant.name + "/" + appp.name + "/" + bd_name + "]"
                            endpoint_data.append((tenant.name, ep.mac, ep.ip, bd_name,
                                                  appp.name, epg.name, epbamconf))

    return aci_subnets, bam_confs, endpoint_data


def start_progress(tenant_info, aci_session):
    """process the progress bar and checks for number of steps"""
    global progress
    global messages
    progress = 0.0

    try:
        step = 100.00 / len(tenant_info)
    except ZeroDivisionError:
        return False
    progress_percent = 0.0

    progress = progress_percent
    messages.put('Starting to import {tenant_number} tenants'.format(tenant_number=len(tenant_info)))
    for tenant, options in tenant_info:
        try:
            process_tenant(aci_session, tenant, override=options['overwrite'],
                           fetch_endpoints=options['import_endpoint_devices'])
        except PortalException:
            message = 'Import completed with some errors for Tenant: {tenant_name}, please check the logs for more' \
                      ' details.'
            message = message.format(tenant_name=tenant.name)
        # pylint: disable=broad-except
        except Exception as e:
            app.logger.exception(str(e))
            message = '{tenant_name} Failed'.format(tenant_name=tenant.name)
        else:
            message = 'Imported Tenant: {tenant_name}'.format(tenant_name=tenant.name)
        progress_percent += step
        progress = round(progress_percent, 2)
        messages.put(message)

    aci_session.close()

    return True


def process_tenant(aci_session, tenant, override=False, fetch_endpoints=False):
    """

    :param aci_session: ACI session
    :param tenant: Cisco Tenant Object
    :param override: Purge existing configurations for this Tenant in BAM
    :param fetch_endpoints: Boolean - Import endpoints
    :return:
    """
    if override:
        purge_tenant(tenant.name)

    create_tenant_tags(tenant.name)

    subnets, configurations, endpoints = fetch_tenant_info(aci_session, tenant, fetch_endpoints)

    configs_has_success = add_configurations(configurations)

    subnets_has_success = add_subnets(subnets)

    endpoints_has_success = add_endpoints(endpoints)

    if configs_has_success and subnets_has_success and endpoints_has_success:
        return True
    else:
        raise PortalException('Tenant import completed with some errors!')


def create_aci_session(aci_apic, aci_user, aci_pass):
    """
    Creates an ACI session from the given APIC address, username, and password.
    :param aci_apic: Address of the APIC.
    :param aci_user: Username for the APIC.
    :param aci_pass: Password for the APIC.
    :return: The ACI session object or raises PortalException on error.
    """
    try:
        aci_session = ACI.Session(aci_apic, aci_user, aci_pass)
    except CredentialsError as e:
        app.logger.error(str(e))
        raise PortalException('ACI credentials or APIC IP invalid.')

    try:
        resp = aci_session.login(timeout=30)
    except (requests.exceptions.MissingSchema, requests.exceptions.InvalidURL, TypeError) as e:
        app.logger.error(str(e))
        raise PortalException('Invalid APIC IP, please provide a correct one.')

    if resp.status_code != 200:
        app.logger.error(resp.content)
        raise PortalException('ACI credentials or APIC IP incorrect!')

    return aci_session


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/cisco_aci/cisco_aci_endpoint')
@util.workflow_permission_required('cisco_aci_page')
@util.exception_catcher
def cisco_aci_cisco_aci_page():
    """
    Renders the form the user would first see when selecting the workflow.

    :return:
    """
    if get_api().get_version() < '9.1.0':
        message = 'Warning! Current BAM version {version} is less than 9.1.0 and Cisco ACI Import will not work!'
        flash(message.format(version=get_api().get_version()))

    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    return render_template(
        'cisco_aci_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )


@route(app, '/cisco_aci/progress')
@util.rest_workflow_permission_required('cisco_aci_page')
def get_progress():
    """
    Endpoint to get the progress information
    :return:
    """
    global messages
    message_list = []
    while not messages.empty():
        try:
            message_list.append(messages.get_nowait())
        except queue.Empty:
            break
    return jsonify({'progress': progress, 'messages': message_list})


# pylint: disable=broad-except
@route(app, '/cisco_aci/import_tenants', methods=['POST'])
@util.rest_workflow_permission_required('cisco_aci_page')
@util.rest_exception_catcher
def cisco_aci_cisco_aci_page_import_tenants():
    """
        Processes the selected Tenants.

        :return:
    """
    global progress
    global messages
    result = get_result_template()

    if get_api().get_version() < '9.1.0':
        message = 'Error! Current BAM version {version} is less than 9.1.0: Infrastructure Import failed!'
        error_message = message.format(version=get_api().get_version())
        result['status'] = FAIL
        result['message'] += error_message
        app.logger.error(error_message)
        return jsonify(empty_decorator(result))

    data = request.form
    result = get_result_template()
    tenant_options = {}
    aci_user = request.form.get('apic_username')
    aci_pass = request.form.get('apic_password')
    aci_apic = request.form.get('apic_ip')
    aci_apic = aci_apic.strip('/')

    try:
        aci_session = create_aci_session(aci_apic, aci_user, aci_pass)
    except PortalException as e:
        result['status'] = FAIL
        result['message'] += str(e)
        return jsonify(empty_decorator(result))

    try:
        check_and_create_tenant_udfs()
    except RESTFault as e:
        message = 'Failed to create UDFs, please check logs for more details.'
        result['status'] = FAIL
        result['message'] += message
        app.logger.error(str(e))
        return jsonify(empty_decorator(result))

    for tenant in data:
        if tenant.endswith('_import'):
            tenant_name = tenant[:-7]
            tenant_import_device = False
            if tenant_name + '_import_endpoint_devices' in data:
                tenant_import_device = True
            tenant_overwrite = False
            if tenant_name + '_overwrite' in data:
                tenant_overwrite = True
            tenant_options[tenant_name] = {'import_endpoint_devices': tenant_import_device,
                                           'overwrite': tenant_overwrite}

    tenants = ACI.Tenant.get(aci_session)
    tenant_info = [(tenant, tenant_options[tenant.name]) for tenant in tenants if tenant.name in tenant_options.keys()]

    if start_progress(tenant_info, aci_session):
        return jsonify('SUCCESS')
    else:
        result['status'] = FAIL
        result['message'] += 'Please select at least one tenant'
        app.logger.error(result['message'])
        return jsonify(empty_decorator(result))


def add_networks_for_fabric(bam_configuration, aci_session):
    """
    Adds networks for the fabric devices
    :param bam_configuration: BAM configuration where the devices are to be imported
    :param aci_session: Cisco ACI session
    :return:
    """

    acitepools = find_teppools(aci_session)
    for acitepool in acitepools:
        try:
            tepool_block = bam_configuration.get_entity_by_cidr(acitepool)
        except PortalException:
            tepool_block = None

        if tepool_block is not None:
            try:
                tepool_block.get_entity_by_cidr(acitepool, tepool_block.IP4Network)
            except PortalException:
                props = "name=Cisco ACI Fabric TEP Network"
                tepool_block.add_ip4_network(acitepool, props)
        else:
            props = "name=Cisco ACI Fabric TEP Block"
            tepool_block = bam_configuration.add_ip4_block_by_cidr(acitepool, props)
            props = "name=Cisco ACI Fabric TEP Network"
            tepool_block.add_ip4_network(acitepool, props)


@route(app, '/cisco_aci/import_fabric', methods=['POST'])
@util.rest_workflow_permission_required('cisco_aci_page')
@util.rest_exception_catcher
def cisco_aci_cisco_aci_page_import_fabric():
    """
        Takes ACI info and imports ACI Fabric.
    """
    global progress
    progress = dict()
    result = get_result_template()

    if get_api().get_version() < '9.1.0':
        message = 'Error! Current BAM version {version} is less than 9.1.0: Fabric Import failed!'
        result['status'] = FAIL
        result['message'] += message.format(version=get_api().get_version())
        return jsonify(empty_decorator(result))

    bam_config_id = request.form.get('configuration', None)
    aci_user = request.form.get('apic_username')
    aci_pass = request.form.get('apic_password')
    aci_apic = request.form.get('apic_ip')
    aci_apic = aci_apic.strip('/')

    try:
        aci_session = create_aci_session(aci_apic, aci_user, aci_pass)
    except PortalException as e:
        result['status'] = FAIL
        result['message'] += str(e)
        return jsonify(empty_decorator(result))

    try:
        check_and_create_fabric_udfs()
    except RESTFault as e:
        message = 'Failed to create UDFs, please check logs for more details.'
        result['status'] = FAIL
        result['message'] += message
        app.logger.error(str(e))
        return jsonify(empty_decorator(result))

    if bam_config_id is not None and request.form.get('import_devices_checkbox', False):
        bam_configuration = get_api().get_entity_by_id(bam_config_id)
        add_networks_for_fabric(bam_configuration, aci_session)
        create_aci_fabric(aci_session, bam_configuration)

    result['status'] = SUCCESS
    result['message'] += 'Successfully imported ACI Fabric'

    aci_session.close()

    return jsonify(empty_decorator(result))


@route(app, '/cisco_aci/form', methods=['POST'])
@util.rest_workflow_permission_required('cisco_aci_page')
@util.rest_exception_catcher
def cisco_aci_cisco_aci_page_form():
    """
        Takes ACI info and returns Tenants in ACI.
    """
    global progress
    progress = dict()

    result = get_result_template()
    aci_user = request.form.get('apic_username')
    aci_pass = request.form.get('apic_password')
    aci_apic = request.form.get('apic_ip')
    aci_apic = aci_apic.strip('/')

    try:
        aci_session = create_aci_session(aci_apic, aci_user, aci_pass)
    except PortalException as e:
        result['status'] = FAIL
        result['message'] += str(e)
        return jsonify(empty_decorator(result))
    else:
        tenants = ACI.Tenant.get(aci_session)

        result['status'] = SUCCESS
        result['message'] += 'Successfully found tenants!'
        result['data'] = {"table_field": raw_table_data()}

        result['data']['table_field']['data'] = populate_table_data(tenants)

        aci_session.close()

    return jsonify(empty_decorator(result))
