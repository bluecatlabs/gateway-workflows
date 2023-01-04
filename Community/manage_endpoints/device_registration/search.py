# Copyright 2022 BlueCat Networks (USA) Inc. and its affiliates. All Rights Reserved.
import os
import sys
import ipaddress
import traceback
import json

from urllib.parse import urlparse
from flask import g, jsonify, make_response, request
from flask_restplus import Resource

from main_app import api

from bluecat import util
from bluecat.entity import Entity
from bluecat.address_manager.internal.db.database import BAMDB

from .common import constant, common
from .common.exception import UserException, NetworkNotFound
from .common.constant import DeviceProperties, NetworkItem, Device, DefaultConfiguration
from .common.database import DeviceDatabase

source_dir = os.path.dirname(__file__)
source_dir = os.path.abspath(source_dir)
if source_dir not in sys.path:
    sys.path.append(source_dir)


search_ns = api.namespace(
    'search',
    path='/configurations/<string:configuration>',
    description='Search operations',
)
TAG_GROUP = common.read_config_file('BAM_CONFIG', "TAG_GROUP")


@search_ns.route('/mac_addresses/<string:mac_address>')
class MacAddressByMacAddress(Resource):
    @util.rest_workflow_permission_required('device_registration_page')
    @api.doc(params={'configuration': 'The name of the configuration',
                     'mac_address': 'The MAC Address',
                     'start': 'start',
                     'count': 'count'})
    @util.no_cache
    def get(self, configuration, mac_address):
        try:
            import config.default_config as config
            default_view = config.default_view if config.default_view else constant.DefaultConfiguration.VIEW_NAME

            start = request.args.get('start', '')
            if start == '':
                start = 1
            count = request.args.get('count', '')
            if count == '':
                count = 100
            start_page = (int(start) - 1) * int(count)
            end_page = start_page + int(count)
            mac_list = []
            device_group = []
            dns_dict = {}
            config = g.user.get_api().get_configuration(configuration)
            mac_object = config.get_mac_address(mac_address)
            device_group_object = common.get_linked_entities_by_admin(mac_object, Entity.Tag)
            for device_group in device_group_object:
                device_group = [device_group.get_name()]
            ip_address_object = common.get_linked_entities_by_admin(mac_object, Entity.IP4Address)
            is_multiple_ip = True if len(ip_address_object) > 1 else False
            if not ip_address_object:
                mac_dict = {
                    Device.Device_id: mac_object.get_id(),
                    Device.Mac_address: mac_address,
                    Device.Name: mac_object.get_name(),
                    Device.Group: device_group[0] if len(device_group) == 1 else device_group,
                    DeviceProperties.Location: mac_object.get_property(
                        DeviceProperties.Location),
                    Device.IS_MULTIPLE_IP: is_multiple_ip,
                    Device.Network: {},
                    Device.Ip_info: {},
                    Device.Domain: {},
                    DeviceProperties.Account_id: mac_object.get_property(
                        DeviceProperties.Account_id),
                    DeviceProperties.Description: mac_object.get_property(
                        DeviceProperties.Description),
                    DeviceProperties.Audit: json.loads(
                        mac_object.get_property(constant.DeviceProperties.Audit).replace("'",
                                                                                                 '"')) if DeviceProperties.Audit in mac_object.get_properties().keys() else [
                        {}]
                }
                mac_list.append(mac_dict)
            for ip_address in ip_address_object:
                network_object = ip_address.get_parent()
                host_record_object = common.get_linked_entities_by_admin(ip_address, Entity.HostRecord)
                ip_address = {
                    Device.Ip_address_id: ip_address.get_id(),
                    Device.Ip_address: ip_address.get_property(DeviceProperties.Address)
                }
                network_detail = {
                    NetworkItem.NAME: network_object.get_name(),
                    constant.NetworkItem.DETAIL: network_object.get_properties()
                }
                if not host_record_object:
                    dns_dict = {}
                for host in host_record_object:
                    view_object = host.get_view()
                    zone = host.get_parent()
                    if view_object.get_name().lower() == default_view:
                        dns_dict = {
                            Device.Host_id: host.get_id(),
                            Device.View: view_object.get_name(),
                            Device.Host_record_name: host.get_property('absoluteName'),
                            Device.Domain_name: zone.get_property('absoluteName')
                        }
                mac_dict = {
                    Device.Device_id: mac_object.get_id(),
                    Device.Mac_address: mac_address,
                    Device.Name: mac_object.get_name(),
                    Device.Group: device_group[0] if len(device_group) == 1 else device_group,
                    DeviceProperties.Location: mac_object.get_property(DeviceProperties.Location),
                    Device.IS_MULTIPLE_IP: is_multiple_ip,
                    Device.Network: network_detail,
                    Device.Ip_info: ip_address,
                    Device.Domain: dns_dict,
                    DeviceProperties.Account_id: mac_object.get_property(DeviceProperties.Account_id),
                    DeviceProperties.Description: mac_object.get_property(DeviceProperties.Description),
                    DeviceProperties.Audit: json.loads(mac_object.get_property(DeviceProperties.Audit).replace("'", '"')) if DeviceProperties.Audit in mac_object.get_properties().keys() else [{}]
                }
                mac_list.append(mac_dict)
            data_length = len(mac_list)
            response = {
                "data": mac_list[start_page:end_page],
                "total": data_length,
                "count": int(count),
                "pagination": {}
            }
            if end_page >= data_length:
                response["pagination"]["next"] = None
                if int(start) > 1:
                    response["pagination"]["previous"] = f"/configurations/{configuration}/mac_addresses/{mac_address}?start={int(start)-1}&count={int(count)}"
                else:
                    response["pagination"]["previous"] = None
            else:
                if int(start) > 1:
                    response["pagination"]["previous"] = f"/configurations/{configuration}/mac_addresses/{mac_address}?start={int(start)-1}&count={int(count)}"
                else:
                    response["pagination"]["previous"] = None
                response["pagination"]["next"] = f"/configurations/{configuration}/mac_addresses/{mac_address}?start={int(start)+1}&count={int(count)}"
            return make_response(jsonify(response), 200)
        except UserException as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 403)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


@search_ns.route('/search_mac_address_by_ip_address')
class MacAddressByIPAddress(Resource):
    @util.rest_workflow_permission_required('device_registration_page')
    @api.doc(params={'configuration': 'The name of the configuration',
                     'ip_address': {'required': True, 'in': 'query', 'description': 'The IP Address'},
                     'start': 'start',
                     'count': 'count'})
    @util.no_cache
    def get(self, configuration):
        try:
            import config.default_config as config
            default_view = config.default_view if config.default_view else constant.DefaultConfiguration.VIEW_NAME

            ip_address = request.args.get('ip_address', '')
            ipaddress.ip_address(ip_address)
            start = request.args.get('start', '')
            if start == '':
                start = 1
            count = request.args.get('count', '')
            if count == '':
                count = 100
            start_page = (int(start) - 1) * int(count)
            end_page = start_page + int(count)
            mac_list = []
            device_group = []
            dns_dict = {}
            config = g.user.get_api().get_configuration(configuration)
            ipv4_address_object = config.get_ip4_address(ip_address)
            mac_address = ipv4_address_object.get_property('macAddress').replace('-', ':')
            location = ipv4_address_object.get_property('locationCode')
            config = g.user.get_api().get_configuration(configuration)
            mac_object = config.get_mac_address(mac_address)
            mac_id = mac_object.get_id()
            mac_name = mac_object.get_name()
            account_id = mac_object.get_property(DeviceProperties.Account_id)
            description = mac_object.get_property(DeviceProperties.Description)
            audit = json.loads(mac_object.get_property(DeviceProperties.Audit).replace("'", '"')) if DeviceProperties.Audit in mac_object.get_properties().keys() else [{}]
            ip_address_object = common.get_linked_entities_by_admin(mac_object, Entity.IP4Address)
            is_multiple_ip = True if len(ip_address_object) > 1 else False
            device_group_object = common.get_linked_entities_by_admin(mac_object, Entity.Tag)
            for device_group in device_group_object:
                device_group = [device_group.get_name()]
            network_object = ipv4_address_object.get_parent()
            network_detail = {
                constant.NetworkItem.NAME: network_object.get_name(),
                constant.NetworkItem.DETAIL: network_object.get_properties()
            }
            network = network_detail
            host_record_object = common.get_linked_entities_by_admin(ipv4_address_object, Entity.HostRecord)
            ip_address = {
                constant.Device.Ip_address_id: ipv4_address_object.get_id(),
                constant.Device.Ip_address: ipv4_address_object.get_property(DeviceProperties.Address)
            }
            for host in host_record_object:
                view_object = host.get_view()
                zone = host.get_parent()
                if view_object.get_name().lower() == default_view:
                    dns_dict = {
                        constant.Device.Host_id: host.get_id(),
                        constant.Device.View: view_object.get_name(),
                        constant.Device.Host_record_name: host.get_property('absoluteName'),
                        constant.Device.Domain_name: zone.get_property('absoluteName')
                    }
            mac_dict = {
                constant.Device.Device_id: mac_id,
                constant.Device.Mac_address: mac_address,
                constant.Device.Name: mac_name,
                constant.Device.Group: device_group[0] if len(device_group) == 1 else device_group,
                constant.DeviceProperties.Location: location,
                constant.Device.IS_MULTIPLE_IP: is_multiple_ip,
                constant.Device.Network: network,
                constant.Device.Ip_info: ip_address,
                constant.Device.Domain: dns_dict,
                constant.DeviceProperties.Account_id: account_id,
                constant.DeviceProperties.Description: description,
                constant.DeviceProperties.Audit: audit
            }
            mac_list.append(mac_dict)
            data_length = len(mac_list)
            response = {
                "data": mac_list[start_page:end_page],
                "total": data_length,
                "count": int(count),
                "pagination": {}
            }
            if end_page >= data_length:
                response["pagination"]["next"] = None
                if int(start) > 1:
                    response["pagination"]["previous"] = f"/configurations/{configuration}/search_mac_address_by_ip_address?ip_address={ip_address}&start={int(start)-1}&count={int(count)}"
                else:
                    response["pagination"]["previous"] = None
            else:
                if int(start) > 1:
                    response["pagination"]["previous"] = f"/configurations/{configuration}/search_mac_address_by_ip_address?ip_address={ip_address}&start={int(start)-1}&count={int(count)}"
                else:
                    response["pagination"]["previous"] = None
                response["pagination"]["next"] = f"/configurations/{configuration}/search_mac_address_by_ip_address?ip_address={ip_address}&start={int(start)+1}&count={int(count)}"
            return make_response(jsonify(response), 200)
        except UserException as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 403)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


@search_ns.route('/search_mac_address_by_name')
class MacAddressByName(Resource):
    @util.rest_workflow_permission_required('device_registration_page')
    @api.doc(params={'configuration': 'The name of the configuration',
                     'name': {'required': True, 'in': 'query', 'description': 'The name of the MAC Address'},
                     'start': 'start',
                     'count': 'count'})
    @util.no_cache
    def get(self, configuration):
        try:
            import config.default_config as config
            default_view = config.default_view if config.default_view else DefaultConfiguration.VIEW_NAME

            name = request.args.get('name', '')
            start = request.args.get('start', '')
            if start == '':
                start = 1
            count = request.args.get('count', '')
            if count == '':
                count = 100
            start_page = (int(start) - 1) * int(count)
            end_page = start_page + int(count)
            mac_list = []
            device_group = []
            network_detail = {}
            ip_address = {}
            dns_dict = {}
            config = g.user.get_api().get_configuration(configuration)
            mac_objects = g.user.get_api().get_entities_by_name(config.get_id(), name, Entity.MACAddress)
            for mac_object in mac_objects:
                device_group_object = common.get_linked_entities_by_admin(mac_object, Entity.Tag)
                for device_group in device_group_object:
                    device_group = [device_group.get_name()]
                ip_address_object = common.get_linked_entities_by_admin(mac_object, Entity.IP4Address)
                is_multiple_ip = True if len(ip_address_object) > 1 else False
                if not ip_address_object:
                    mac_dict = {
                        Device.Device_id: mac_object.get_id(),
                        Device.Mac_address: mac_object.get_property(DeviceProperties.Address).replace('-', ':'),
                        Device.Name: name,
                        Device.Group: device_group[0] if len(device_group) == 1 else device_group,
                        DeviceProperties.Location: mac_object.get_properties().get(
                            DeviceProperties.Location),
                        Device.IS_MULTIPLE_IP: is_multiple_ip,
                        Device.Network: {},
                        Device.Ip_info: {},
                        Device.Domain: {},
                        DeviceProperties.Account_id: mac_object.get_property(DeviceProperties.Account_id),
                        DeviceProperties.Description: mac_object.get_property(DeviceProperties.Description),
                        DeviceProperties.Audit: json.loads(
                            mac_object.get_property(DeviceProperties.Audit).replace("'",
                                                                                                     '"')) if DeviceProperties.Audit in mac_object.get_properties().keys() else [
                            {}]
                    }
                    mac_list.append(mac_dict)
                for ip_address in ip_address_object:
                    network_object = ip_address.get_parent()
                    host_record_object = common.get_linked_entities_by_admin(ip_address, Entity.HostRecord)
                    ip_address = {
                        Device.Ip_address_id: ip_address.get_id(),
                        Device.Ip_address: ip_address.get_property(DeviceProperties.Address)
                    }
                    network_detail = {
                        NetworkItem.NAME: network_object.get_name(),
                        NetworkItem.DETAIL: network_object.get_properties()
                    }
                    if not host_record_object:
                        dns_dict = {}
                    for host in host_record_object:
                        view_object = host.get_view()
                        zone = host.get_parent()
                        if view_object.get_name().lower() == default_view:
                            dns_dict = {
                                Device.Host_id: host.get_id(),
                                Device.View: view_object.get_name(),
                                Device.Host_record_name: host.get_property('absoluteName'),
                                Device.Domain_name: zone.get_property('absoluteName')
                            }
                    mac_dict = {
                        Device.Device_id: mac_object.get_id(),
                        Device.Mac_address: mac_object.get_property(DeviceProperties.Address).replace('-', ':'),
                        Device.Name: name,
                        Device.Group: device_group[0] if len(device_group) == 1 else device_group,
                        DeviceProperties.Location: mac_object.get_property(DeviceProperties.Location),
                        Device.IS_MULTIPLE_IP: is_multiple_ip,
                        Device.Network: network_detail,
                        Device.Ip_info: ip_address,
                        Device.Domain: dns_dict,
                        DeviceProperties.Account_id: mac_object.get_property(DeviceProperties.Account_id),
                        constant.DeviceProperties.Description: mac_object.get_property(DeviceProperties.Description),
                        constant.DeviceProperties.Audit: json.loads(
                            mac_object.get_property(DeviceProperties.Audit).replace("'",
                                                                                                     '"')) if DeviceProperties.Audit in mac_object.get_properties().keys() else [
                            {}]
                    }
                    mac_list.append(mac_dict)
            data_length = len(mac_list)
            response = {
                "data": mac_list,
                "total": data_length,
                "count": int(count),
                "pagination": {}
            }
            if end_page >= data_length:
                response["pagination"]["next"] = None
                if int(start) > 1:
                    response["pagination"]["previous"] = f"/configurations/{configuration}/search_mac_address_by_name?name={name}&start={int(start)-1}&count={int(count)}"
                else:
                    response["pagination"]["previous"] = None
            else:
                if int(start) > 1:
                    response["pagination"]["previous"] = f"/configurations/{configuration}/search_mac_address_by_name?name={name}&start={int(start)-1}&count={int(count)}"
                else:
                    response["pagination"]["previous"] = None
                response["pagination"]["next"] = f"/configurations/{configuration}/search_mac_address_by_name?name={name}&start={int(start)+1}&count={int(count)}"
            return make_response(jsonify(response), 200)
        except UserException as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 403)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


@search_ns.route('/mac_addresses')
class MacAddress(Resource):
    @util.rest_workflow_permission_required('device_registration_page')
    @api.doc(params={'configuration': 'The name of the configuration',
                     'device_group': {'required': True, 'in': 'query', 'description': 'The name of the device group'},
                     'device_location': {'required': True, 'in': 'query', 'description': 'The name of the device location'},
                     'ip_network': 'The IPNetwork range',
                     'dns_domain': 'The DNS domain',
                     'account_id': 'The Account ID',
                     'start': 'start',
                     'count': 'count',
                     'start_index': 'start_index'})
    @util.no_cache
    def get(self, configuration):
        try:
            import config.default_config as config

            device_group = request.args.get('device_group', '')
            device_location = request.args.get('device_location', '')
            ip_network = request.args.get('ip_network', '')
            dns_domain = request.args.get('dns_domain', '')
            dns_domain_value = dns_domain.lower()
            config = g.user.get_api().get_configuration(configuration)
            if dns_domain.endswith("."):
                dns_domain_value = dns_domain_value[:-1]
            account_id = request.args.get('account_id', '')
            start = request.args.get('start', '')
            if start == '':
                start = 1
            count = request.args.get('count', '')
            if count == '':
                count = 100
            count_index = request.args.get('start_index', '')
            if not count_index:
                count_index = 0
            count_index = int(count_index)
            start_page = (int(start) - 1) * int(count)
            end_page = start_page + int(count)

            tag_group_obj = g.user.get_api().get_tag_group_by_name(TAG_GROUP)
            device_group_id = tag_group_obj.get_tag_by_name(device_group).id

            address_parts = urlparse(g.user.get_api().get_url())
            db_host = address_parts.netloc
            bam_db = BAMDB(db_host, g.user.logger)
            device_db = DeviceDatabase(bam_db)
            devices = device_db.get_device(tag=device_group_id, config=config.get_id(), location=device_location,
                                           network=ip_network, dns_domain=dns_domain_value, account_id=account_id)

            data_length = len(devices)
            response = {
                "data": devices,
                "start_index": count_index,
                "total": data_length,
                "count": int(count),
                "pagination": {}
            }
            ### Need optimize coding style
            if end_page >= data_length:
                response["pagination"]["next"] = None
                if int(start) > 1:
                    response["pagination"][
                        "previous"] = f"/configurations/{configuration}/mac_addresses?device_group={device_group}&device_location={device_location}&ip_network={ip_network}&dns_domain={dns_domain}&start={int(start) - 1}&count={int(count)}"
                else:
                    response["pagination"]["previous"] = None
            else:
                if int(start) > 1:
                    response["pagination"][
                        "previous"] = f"/configurations/{configuration}/mac_addresses?device_group={device_group}&device_location={device_location}&ip_network={ip_network}&dns_domain={dns_domain}&start={int(start) - 1}&count={int(count)}"
                else:
                    response["pagination"]["previous"] = None
                response["pagination"][
                    "next"] = f"/configurations/{configuration}/mac_addresses?device_group={device_group}&device_location={device_location}&ip_network={ip_network}&dns_domain={dns_domain}&start={int(start) + 1}&count={int(count)}"
            return make_response(jsonify(response), 200)
        except NetworkNotFound as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 403)
        except UserException as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 403)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)
