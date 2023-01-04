# Copyright 2022 BlueCat Networks (USA) Inc. and its affiliates. All Rights Reserved.
import json, traceback, time
from flask import g, jsonify, make_response, request
from flask_restplus import Resource

from bluecat import util, constants
from bluecat.api_exception import BAMException, PortalException
from bluecat.entity import Entity
from bluecat.util import map_to_properties
from main_app import api
from .libs.model.mac_address_models import mac_address_model, mac_address_meta_update_model
from .libs.parse.mac_address_parsers import mac_address_parser, mac_address_meta_update_parser
from .common.constant import Device, DeviceProperties, DeviceAudit, DeviceAction, DEPLOY_PROPERTIES
from .common.common import get_current_date_time, read_config_file

mac_address_ns = api.namespace(
    'mac_address',
    path='/configurations/<string:configuration>',
    description='MAC Address operations',
)
TAG_GROUP = read_config_file('BAM_CONFIG', "TAG_GROUP")


@mac_address_ns.route('/mac_address/')
class MacAddress(Resource):

    @util.rest_workflow_permission_required('device_registration_page')
    @util.no_cache
    @mac_address_ns.expect(mac_address_model, validate=True)
    @mac_address_ns.response(422, 'Error in POST data')
    @mac_address_ns.response(409, 'MAC address already exists')
    def post(self, configuration):
        """ Add a new Device, represented by MAC Address. """
        api = g.user.get_api()
        config_obj = api.get_configuration(configuration)
        try:
            data = mac_address_parser.parse_args()
            device_mac_address = data.get(Device.Mac_address, '')
            device_name = data.get(Device.Name, '')
            device_group = data.get(Device.Group, '')
            device_location = data.get(Device.Location, '')
            device_ip_address = data.get(Device.Ip_address, '')
            device_domain = data.get(Device.Domain, '')
            device_account_id = data.get(Device.Account_id, '')
            device_description = data.get(Device.Description, '')

            if device_domain:
                zones = config_obj.get_zones_by_hint(device_domain)
                if zones:
                    zone_obj = zones[0]
                else:
                    return "Zone with name {} is not locate in default configuration".format(device_domain), 404
                if zone_obj:
                    if zone_obj.get_property("absoluteName") != device_domain:
                        return "Zone with name {} not found".format(device_domain), 404
                if zone_obj.get_host_record(device_name):
                    return "Host record with name {} already existed".format(device_name), 409
            device_audit = [
                {
                    DeviceAudit.User: g.user.get_username(),
                    DeviceAudit.Action: DeviceAction.CREATE,
                    DeviceAudit.DateTime: get_current_date_time()
                }
            ]
            device_properties = {
                DeviceProperties.Account_id: str(device_account_id),
                DeviceProperties.Description: str(device_description),
                DeviceProperties.Address: str(device_mac_address),
                DeviceProperties.Audit: str(device_audit),
                DeviceProperties.Location: str(device_location),
            }
            device_properties = map_to_properties(device_properties)
            try:
                mac_address_obj = config_obj.add_mac_address(address=device_mac_address,
                                                             name=device_name, properties=device_properties)
            except BAMException as e:
                if "Duplicate of another item" in str(e):
                    return "MAC address {} already existed".format(device_mac_address), 409
                return str(e), 500
            tag_group_obj = api.get_tag_group_by_name(TAG_GROUP)
            device_group_obj = tag_group_obj.get_tag_by_name(device_group)
            mac_address_obj.link_entity(entity_id=device_group_obj.id)

            if device_ip_address:
                ip_address_properties = "name=" + device_name
                device_ip_address_obj = config_obj.assign_ip4_address(
                        address=device_ip_address,
                        mac_address=device_mac_address,
                        hostinfo="",
                        action=constants.IPAssignmentActionValues.MAKE_DHCP_RESERVED,
                        properties=ip_address_properties
                    )
                if device_domain:
                    zone_obj = config_obj.get_zones_by_hint(device_domain)[0]
                    if zone_obj:
                        if zone_obj.get_property("absoluteName") != device_domain:
                            return "Zone with name {} not found".format(device_domain), 404
                        try:
                            host_record_obj = zone_obj.add_host_record(name=device_name, addresses=[device_ip_address])
                            host_record_obj._api.selective_deploy([host_record_obj.get_id()], DEPLOY_PROPERTIES)
                        except BAMException as e:
                            if "Duplicate of another item" in str(e):
                                return "Host record with name {} already existed".format(device_name), 409

            return jsonify(mac_address_obj.to_json()), 200
        except BAMException as e:
            if "Object was not found" in str(e):
                return str(e), 404
            if "IP Address doesn't belong to a Network." in str(e):
                return str(e), 404
            return str(e), 500
        except PortalException as e:
            if "malformed properties string" in str(e):
                return str(e), 500
            return str(e), 404
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return str(e), 500

    @util.rest_workflow_permission_required('device_registration_page')
    @util.no_cache
    @mac_address_ns.expect(mac_address_meta_update_model, validate=True)
    @mac_address_ns.response(422, 'Error in PATCH data')
    @mac_address_ns.response(409, 'MAC address already exists')
    def patch(self, configuration):
        """ Update Device's meta data. """
        api = g.user.get_api()
        config_obj = api.get_configuration(configuration)
        try:
            data = mac_address_meta_update_parser.parse_args()
            device_mac_address = data.get(Device.Mac_address, '')
            device_name_update = data.get(Device.Name, '')
            device_ip_address_id_update = data.get(Device.Ip_address_id, '')
            device_host_record_id_update = data.get(Device.Host_id, '')
            device_account_id_update = data.get(Device.Account_id, '')
            device_description_update = data.get(Device.Description, '')

            mac_address_obj = config_obj.get_mac_address(device_mac_address)
            device_name = mac_address_obj.get_name()
            device_account_id = mac_address_obj.get_property(DeviceProperties.Account_id)
            device_description = mac_address_obj.get_property(DeviceProperties.Description)
            device_audit = mac_address_obj.get_property(DeviceProperties.Audit)

            device_description = device_description_update
            device_account_id = device_account_id_update
            if device_name_update and device_name_update != device_name:
                device_name = device_name_update
                if device_host_record_id_update:
                    try:
                        host_record_obj = g.user.get_api().get_entity_by_id(device_host_record_id_update)
                        host_record_obj.set_name(device_name_update)
                        host_record_obj.update()
                        time.sleep(1)
                        host_record_obj._api.selective_deploy([host_record_obj.get_id()], DEPLOY_PROPERTIES)
                    except BAMException as e:
                        if "Duplicate of another item" in str(e):
                            return "Host record with name {} already existed".format(device_name), 409
                if device_ip_address_id_update:
                    ip_address_obj = g.user.get_api().get_entity_by_id(device_ip_address_id_update)
                    ip_address_obj.set_name(device_name)
                    ip_address_obj.update()
                mac_address_obj.set_name(device_name_update)

            if not device_audit:
                device_audit = []
            else:
                device_audit = json.loads(device_audit.replace("'", '"'))

            device_update = {
                DeviceAudit.User: g.user.get_username(),
                DeviceAudit.Action: DeviceAction.UPDATE,
                DeviceAudit.DateTime: get_current_date_time()
            }
            if len(device_audit) >= 5:
                del device_audit[1]
            device_audit.append(device_update)

            device_properties = {
                DeviceProperties.Account_id: str(device_account_id),
                DeviceProperties.Description: str(device_description),
                DeviceProperties.Audit: str(device_audit),
            }
            mac_address_obj.set_properties(device_properties)
            mac_address_obj.update()

            return jsonify(device_audit), 200

        except BAMException as e:
            if "Object was not found" in str(e):
                return str(e), 404
            if "IP Address doesn't belong to a Network." in str(e):
                return str(e), 404
            return str(e), 500
        except PortalException as e:
            if "malformed properties string" in str(e):
                return str(e), 500
            return str(e), 404
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            if "Unable to determine the server for DNS Selective Deploy" in str(e):
                return "Unable to determine the server for DNS Selective Deploy", 500

    @util.rest_workflow_permission_required('device_registration_page')
    @mac_address_ns.expect(mac_address_model, validate=True)
    @mac_address_ns.response(500, "Invalid input")
    @util.no_cache
    @api.doc(params={'configuration': 'The name of the configuration',
                     'is_multiple_ip': 'True to delete the device, False to unassigned device. Default False'})
    def delete(self, configuration):
        try:
            api = g.user.get_api()
            config = api.get_configuration(configuration)
            data = mac_address_parser.parse_args()
            device_mac_address = data.get(Device.Mac_address, '')
            device_ip_address = data.get(Device.Ip_address, '')
            is_multiple = request.args.get(Device.IS_MULTIPLE_IP, 1)
            try:
                mac_address = config.get_mac_address(device_mac_address)
            except BAMException as ex:
                if 'object exist' in str(ex):
                    raise 'No MAC Adress object exist with MAC address: {}'.format(device_mac_address)
            assign_ip_addresses = list(mac_address.get_linked_entities(Entity.IP4Address))
            if mac_address:
                if device_ip_address:
                    flag = False
                    if assign_ip_addresses:
                        for ip in assign_ip_addresses:
                            flag = True
                            ip_address = ip.get_property("address")
                            if device_ip_address == ip_address:
                                ip_address = config.get_ip4_address(device_ip_address)
                                host_records_objs = list(ip_address.get_linked_entities(Entity.HostRecord))
                                if host_records_objs:
                                    api.selective_deploy(host_records_objs, DEPLOY_PROPERTIES)
                                ip_address.delete()
                                time.sleep(1)  # Waiting for BAM to deploy change to server
                                if not is_multiple == 0:
                                    mac_address.delete()
                                return make_response("Delete successful!")
                        if not flag:
                            return make_response("Mac address was not assign to ip {}".format(device_ip_address), 400)
                    return make_response(jsonify("MAC address was not assign to any ip address"), 400)
                else:
                    if assign_ip_addresses:
                        return make_response("Mac address is assigned to another ip!Please insert ip address!")
                    else:
                        mac_address.delete()
                        return "Delete successful!"
            return make_response(jsonify("Require mac address and ip address", 400))
        except (BAMException, PortalException) as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 403)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)
