# Copyright 2022 BlueCat Networks (USA) Inc. and its affiliates. All Rights Reserved.
import configparser
import os
import requests
from datetime import datetime
from cryptography.fernet import InvalidToken

from flask import g

from bluecat.util.util import decrypt_key
from bluecat.entity import Entity
from bluecat.api_exception import BAMException
from bluecat_libraries.http_client import GeneralError
from bluecat.util import has_response
from .constant import CONFIG_PATH, DeviceAudit, Preference, NetworkItem, DnsItem, LocationItem, UDF, AccessRight, UserType, CONFIG, PROPERTY, DefaultConfiguration, DEFAULT_COUNT


def read_config_file(section, setting_name, default_value='no'):
    config = configparser.ConfigParser()
    config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), CONFIG_PATH)))
    try:
        data = config[section]
        value = data.get(setting_name, default_value).strip()
    except (configparser.NoSectionError, KeyError):
        value = default_value
    return value


def decrypt_credential(encrypted_password):
    try:
        password = decrypt_key(encrypted_password.encode()) if encrypted_password else ""
    except InvalidToken:
        password = ""
        return password
    except Exception as e:
        g.user.logger.debug("common.decrypt_credential - encrypted_password: {} raise {}".format(
            encrypted_password, e
        ))
        password = ""
    return password


def generate_zone_fqdn(zone=None, view=None, data=None):
    if view is not None:
        if zone is None:
            if data is not None:
                if 'absolute_name' in data.keys():
                    return data['absolute_name']
        elif '/zone' not in zone:
            zone_split = zone.split('.')
            zone_split.reverse()
            current = view
            for z in zone_split:
                current = current.get_zone(z)
            if data is not None:
                return data['absolute_name'].split('.')[0] + '.' + current.get_full_name()
            else:
                return current
        else:
            zone_parent = view
            zone_hierarchy = zone.split('/zones')
            zone_entity = zone_parent.get_zone(zone_hierarchy[0])
            zone = check_zone_in_path(zone_entity, zone_hierarchy[0], zone_hierarchy[1:], zone_parent)
            if data is not None:
                return data['absolute_name'].split('.')[0] + '.' + zone.get_full_name()
            else:
                return zone


def check_zone_in_path(zone_entity, pre_path, post_path, zone_parent, delimiter='/zones'):
    """Because "/" characters can be in the zone name, need to check if the "/" in the path is part of zone name or not
    """
    if not post_path:
        return zone_entity

    if zone_entity is not None:
        new_pre_path = post_path[0]
        if new_pre_path.startswith('/'):
            new_pre_path = new_pre_path[1:]
        sub_zone = zone_entity.get_zone(new_pre_path)
        final_result = check_zone_in_path(sub_zone, new_pre_path, post_path[1:], zone_entity)
        if final_result is not None:
            return final_result
    pre_path += delimiter + post_path.pop(0)

    zone = zone_parent.get_zone(pre_path)
    if zone is not None:
        final_result = check_zone_in_path(zone, pre_path, post_path, zone_parent)
        if final_result is not None:
            return final_result
    else:
        return None


admin_username = os.environ.get("ADMIN_USERNAME", "")
if not admin_username:
    admin_username = read_config_file(CONFIG.BAM_CONFIG, CONFIG.ADMIN_USERNAME)
encrypted_admin_password = os.environ.get("ADMIN_PASSWORD", "")
if not encrypted_admin_password:
    encrypted_admin_password = read_config_file(CONFIG.BAM_CONFIG, CONFIG.ADMIN_PASSWORD)
admin_password = decrypt_credential(encrypted_admin_password)


def get_locations_and_dns_and_networks(tag_groups_name, tag_name):
    """Get location and dns and network through a tag group in a same defined configuration with format:
    Preference item always appear in the top of the list
        [
            "location_code_1":  {
                "DNS_domain":  [
                                "example.com",
                                "test.example.com"
                                ],
                "IP4Network" :  {
                                "name" : "network_name",
                                "detail": {
                                    detail: detail_value,
                                    ...
                                },
                                "next_ip": next available ip
                                },
                "Location_name": "location_name"
            },...
        ]
    """
    g.user.logger.info(
        "common.get_location_and_dns_and_network_from_tag_group - tag_groups_name: {} - tag_name: {}".format(
            tag_groups_name, tag_name))
    result = []
    tag = None
    try:
        import config.default_config as config
        default_configuration = config.default_configuration if config.default_configuration else DefaultConfiguration.CONFIG_NAME
        default_view = config.default_view if config.default_view else DefaultConfiguration.VIEW_NAME
        tags = get_tags_from_tag_group(tag_groups_name)
        for entity in tags:
            if tag_name == entity.get_name():
                tag = entity
                break
        if not tag:
            return result
        user = g.user.get_api().get_user(g.user.get_username())
        user_id = user.get_id()
        locations = []
        user_type = user.get_property(UserType.TYPE)
        linked_networks = get_linked_entities_by_admin(tag, Entity.IP4Network)
        linked_dns_zone = get_linked_entities_by_admin(tag, Entity.Zone)
        is_admin = False
        if user_type == UserType.ADMIN:
            is_admin = True
        linked_dns_zone = rm_dns_with_no_access_right(linked_dns_zone, user, user_id, default_view, is_admin)
        for network in linked_networks:
            old_session = None
            try:
                if user_type == UserType.REGULAR:
                    old_session = login_admin_session(network, admin_username, admin_password)
                    if network.get_access_right(user_id).get_value() == AccessRight.HIDE:
                        logout_admin_session(network, old_session)
                        continue
                if network.get_parent_of_type(Entity.Configuration).get_name() != default_configuration:
                    if user_type == UserType.REGULAR:
                        logout_admin_session(network, old_session)
                    continue
                location_network = network.get_property(PROPERTY.LOCATION_CODE)
                if not location_network:
                    g.user.logger.debug('[SKIP] Network CIDR: {} not have location code.'.format(
                        network.get_property(PROPERTY.CIDR)))
                    if user_type == UserType.REGULAR:
                        logout_admin_session(network, old_session)
                    continue
                network_item = {
                    NetworkItem.NAME: network.get_name(),
                    NetworkItem.DETAIL: network.get_properties(),
                    NetworkItem.NEXT_IP: network.get_next_available_ip4_address()
                }
                item = {
                    location_network:
                        {
                            DnsItem.DNSITEM: [],
                            NetworkItem.NETWORKITEM: [network_item],
                            LocationItem.LOCATIONITEM: g.user.get_api().get_location_by_code(location_network).get_name()
                        }
                }
                location_obj = g.user.get_api().get_location_by_code(location_network)
                location_preference = location_obj.get_property(UDF.PREFERENCE)
                if location_network not in locations:
                    locations.append(location_network)
                    if location_preference == Preference.TRUE:
                        result.insert(0, item)
                    else:
                        result.append(item)
                else:
                    for item in result:
                        added_flag = False
                        for key in item:
                            if location_network == key:
                                added_flag = True
                                if network.get_property(UDF.PREFERENCE) == Preference.TRUE:
                                    item[location_network][NetworkItem.NETWORKITEM].insert(0, network_item)
                                else:
                                    item[location_network][NetworkItem.NETWORKITEM].append(network_item)
                                break
                        if added_flag:
                            break
                if old_session:
                    logout_admin_session(network, old_session)
            except Exception as e:
                logout_admin_session(network, old_session)
                raise e
        for dns_domain in linked_dns_zone:
            old_session = None
            try:
                if user_type == UserType.REGULAR:
                    old_session = login_admin_session(dns_domain, admin_username, admin_password)
                    if dns_domain.get_access_right(user_id).get_value() == AccessRight.HIDE:
                        logout_admin_session(dns_domain, old_session)
                        continue
                    logout_admin_session(dns_domain, old_session)
                if dns_domain.get_parent_of_type(Entity.Configuration).get_name() != default_configuration:
                    if user_type == UserType.REGULAR:
                        logout_admin_session(dns_domain, old_session)
                    continue
                locations_dns_domain = dns_domain.get_property(UDF.LOCATIONCODE)
                if locations_dns_domain:
                    locations_dns_domain = dns_domain.get_property(UDF.LOCATIONCODE).split(',')
                    for location_dns_domain in locations_dns_domain:
                        for item in result:
                            added_flag = False
                            for key in item:
                                if location_dns_domain == key:
                                    added_flag = True
                                    if dns_domain.get_property(UDF.PREFERENCE) == Preference.TRUE:
                                        item[key][DnsItem.DNSITEM].insert(0, dns_domain.get_property(PROPERTY.ABS_NAME))
                                    else:
                                        item[key][DnsItem.DNSITEM].append(dns_domain.get_property(PROPERTY.ABS_NAME))
                                    break
                            if added_flag:
                                break
                else:
                    for item in result:
                        for key in item:
                            if dns_domain.get_property(UDF.PREFERENCE) == Preference.TRUE:
                                item[key][DnsItem.DNSITEM].insert(0, dns_domain.get_property(PROPERTY.ABS_NAME))
                            else:
                                item[key][DnsItem.DNSITEM].append(dns_domain.get_property(PROPERTY.ABS_NAME))
                if old_session:
                    logout_admin_session(dns_domain, old_session)
            except Exception as e:
                logout_admin_session(dns_domain, old_session)
                raise e
        rm_list = []
        for item in result:
            for key in item:
                if not item[key][DnsItem.DNSITEM]:
                    rm_list.append(item)
        for item in rm_list:
            result.remove(item)
        return result
    except Exception as e:
        g.user.logger.debug(
            "common.get_location_and_dns_and_network_from_tag_group - tag_groups_id: {} - tag_name: {} failed! {}".format
            (tag_groups_name, tag_name, str(e)))
        raise e


def rm_dns_with_no_access_right(linked_dns_zone, user, user_id, default_view, is_admin=False):
    rm_dns_list = []
    old_session = None
    for dns_zone in linked_dns_zone:
        if not is_admin:
            old_session = login_admin_session(dns_zone, admin_username, admin_password)
        if user.get_property(UserType.TYPE) == UserType.REGULAR:
            if dns_zone.get_access_right(user_id).get_value() == AccessRight.HIDE:
                rm_dns_list.append(dns_zone)
                continue
        view_linked_dns_zone = dns_zone.get_parent_of_type(Entity.View)
        if view_linked_dns_zone.get_name() != default_view:
            rm_dns_list.append(dns_zone)
        if not is_admin and old_session:
            logout_admin_session(dns_zone, old_session)
    for rm_dns in rm_dns_list:
        linked_dns_zone.remove(rm_dns)
    return linked_dns_zone


def get_tags_from_tag_group(tag_group_name):
    try:
        tag_groups = g.user.get_api().get_tag_group_by_name(tag_group_name)
        tags = list(g.user.get_api().get_entities(tag_groups.get_id(), Entity.Tag))
        result = []
        for tag in tags:
            if tag.get_property(UDF.PREFERENCE) == Preference.TRUE:
                result.insert(0, tag)
            else:
                result.append(tag)
        return result
    except Exception as e:
        g.user.logger.debug("common.get_tags_from_tag_group - tag_group_name: {} failed! {}".format(
            tag_group_name, str(e)))
        raise e


def get_current_date_time():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt_string


def audit_list_to_string(audit_list):
    audit_string = ''
    for session in audit_list:
        session_string = session.get(DeviceAudit.User) + ',' + session.get(DeviceAudit.Action) + ',' + session.get(
            DeviceAudit.DateTime)
        audit_string += session_string
        audit_string += '.'
    return audit_string


def audit_string_to_list(audit_string):
    audit_data = audit_string.split('.')
    audit_data = audit_data[: -1]
    audit_list = []
    for session in audit_data:
        data = session.split(',')
        session_dict = {
            DeviceAudit.User: data[0],
            DeviceAudit.Action: data[1],
            DeviceAudit.DateTime: data[2]
        }
        audit_list.append(session_dict)
    return audit_list


def login_admin_session(entity, username, password):
    try:
        old_session = entity._raw_api.session
        new_session = requests.Session()
        new_session.verify = False
        entity._raw_api.session = new_session
        entity._raw_api.login(username, password)
        g.user.logger.info("Switching to admin session {}".format(username))
        return old_session
    except Exception as e:
        if "Connection Error!" in str(e):
            raise Exception("Please provide admin credential!")
        g.user.logger.debug("common.login_admin_session- entity: {}, username: {} raise e".format(entity, username))
        raise e




def logout_admin_session(entity, previous_session):
    if previous_session:
        g.user.logger.info("Switching back to {}".format(g.user.get_username()))
        entity._raw_api.session = previous_session


def get_linked_entities(entity, entity_type, start=0, count=DEFAULT_COUNT.DEFAULT_MAX_COUNT):
    """
        Get all the linked entities of a given type with more config
        entity_type: children identity to get more config
        start: start index
        count: max count
        :return: Iterator  for a given type entities.
    """
    try:
        data = entity._raw_api.getLinkedEntities(entity.get_id(), entity_type, start, count)
    except GeneralError as e:
        raise BAMException(str(e)) from e
    if not has_response(data):  # Detect fake non-empty responses.
        return []
    return [entity._api.instantiate_entity(item) for item in data]


def get_children_of_type(entity, entity_type, start=0, count=DEFAULT_COUNT.DEFAULT_MAX_COUNT):
    """
        Get all the children entities of a given type with more config
        entity_type: children identity to get more config
        start: start index
        count: max count
        :return: Iterator  for a given type entities.
    """
    try:
        data = entity._raw_api.getEntities(entity.get_id(), entity_type, start, count)
    except GeneralError as e:
        raise BAMException(str(e)) from e
    if not has_response(data):  # Detect fake non-empty responses.
        return []
    return [entity._api.instantiate_entity(item) for item in data]


def get_linked_entities_by_admin(entity, entity_type: Entity, start=0, count=DEFAULT_COUNT.DEFAULT_MAX_COUNT):
    old_session = None
    try:
        result = get_linked_entities(entity, entity_type, start, count)
        return result
    except Exception as e:
        if "could not extract ResultSet" in str(e):
            try:
                old_session = login_admin_session(entity, admin_username, admin_password)
                result = get_linked_entities(entity, entity_type, start, count)
                logout_admin_session(entity, old_session)
                return result
            except Exception as e:
                if old_session:
                    logout_admin_session(entity, old_session)
                g.user.logger.debug("common.get_linked_entities_by_admin - entity: {}, entity_type: {} raise {}".format(
                    entity, entity_type, str(e)))
                raise e
        else:
            g.user.logger.debug("common.get_linked_entities_by_admin - entity: {}, entity_type: {} raise {}".format(
                entity, entity_type, str(e)))
        raise e
