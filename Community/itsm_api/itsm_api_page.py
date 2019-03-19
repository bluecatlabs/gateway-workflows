# Copyright 2018 BlueCat Networks. All rights reserved.

from flask import request, g, abort, jsonify
import bluecat.server_endpoints as se
from bluecat import route, util
from main_app import app
from bluecat.api_exception import PortalException, BAMException

exceptions = (BAMException, Exception, PortalException)
wf_name = "itsm_api"


####################################################################################################
# External APIs
#
# All of these just wrap the functions for external use
####################################################################################################


@route(app, '/%s/get_bc_data' % (wf_name), methods=['GET'])
@util.rest_workflow_permission_required('itsm_api_page')
@util.rest_exception_catcher
def get_bc_data_api():
    data = get_bc_data()
    return jsonify({"data" : data, "status":"SUCCESS"})


@route(app, '/%s/get_zones' % (wf_name), methods=['POST'])
@util.rest_workflow_permission_required('itsm_api_page')
@util.rest_exception_catcher
def get_zones_api():
    request_json = get_json(request)
    if request_json is None:
        return no_data()
    data = get_zones(request_json)
    return jsonify(data)

@route(app, '/%s/validate_ip' % (wf_name), methods=['POST'])
@util.rest_workflow_permission_required('itsm_api_page')
@util.rest_exception_catcher
def validate_ip_api():
    request_json = get_json(request)
    if request_json is None:
        return no_data()
    data = validate_ip(request_json)
    return jsonify(data)

@route(app, '/%s/assign_record' % (wf_name), methods=['POST'])
@util.rest_workflow_permission_required('itsm_api_page')
@util.rest_exception_catcher
def assign_record_api():
    request_json = get_json(request)
    if request_json is None:
        return no_data()
    data = assign_record(request_json)
    return jsonify(data)


####################################################################################################
# Internal APIs
#
# All of these do the BAM interactions. System administration only in these. External APIs will wrap
# one or more of these paired with business logic
####################################################################################################


def assign_record(json):
    configuration = get_key(json, "configuration")
    ip = get_key(json, "ip")
    view_name = get_key(json, "view")
    fqdn = get_key(json, "record")
    if None in (fqdn, view_name, ip, configuration):
        return {
            "data": {},
            "message": "Missing one or more input",
            "status": "FAIL"
        }
    # split record from zone
    record, zone_name = split_fqdn(fqdn)
    config, view, zone, message = get_config_view_zone(configuration, view_name, zone_name)
    if config is False or view is False:
        return {
            "data": {},
            "message": message,
            "status": "FAIL"
        }

    #Does the IP exist?
    #We check true to duplicate record points, true to create if not exists
    ip_exists = does_ip_exist(ip, config, False, True)
    app.logger.info("IP existence: %s" % str(ip_exists))

    if ip_exists:
        try:
            record = view.add_host_record(fqdn, [ip])
            print(record)
        except exceptions as e:
            app.logger.error(str(e))
            if "Duplicate of another item" in str(e):
                return {"data": {}, "status":"FAIL", "message": "Duplicate record"}
            else:
                return {"data": {}, "status":"FAIL", "message": "Unable to add record"}
    else:
        return {"data": {}, "status":"FAIL",  "message": "IP is not invalid"}
    return {"data": {}, "status":"SUCCESS",  "message": ""}


def validate_ip(json):
    configuration = get_key(json, "configuration")
    ip = get_key(json, "ip")
    if ip is None or configuration is None:
        return {"data": {}, "message":"Missing one or more inputs", "status":"FAIL"}

    try:
        result = se.get_address_data(configuration, ip)
        return result
    except:
        return {"data":{}, "status":"FAIL", "message":"IP not found"}


def get_zones(json):
    configuration = get_key(json, "configuration")
    view_name = get_key(json, "view")
    zone = get_key(json, "zone")

    if None in (view_name, configuration):
        return {
            "data": {},
            "message": "Invalid view or configuration",
            "status": "FAIL"
        }
    try:
        zones = se.get_zones_data_by_hint(configuration, view_name, zone)
        return zones
    except:
        return {
            "data": {},
            "message": "Invalid inputs, do better.",
            "status": "FAIL"
        }


def get_bc_data():
    configurations = g.user.get_api().get_configurations()
    data = {}
    for configuration in configurations:
        data[configuration.name] = {"id":configuration.get_id(), "views":[]}
        views = configuration.get_views()
        for view in views:
            data[configuration.name]["views"].append(view.name)
    return data


####################################################################################################
# Internal functions
#
# Individual pieces never to be used directly by an external API
####################################################################################################


def get_config_view_zone(configuration, view_name, zone_name):
    try:
        config = g.user.get_api().get_entity_by_id(configuration)
    except Exception as e:
        app.logger.error(str(e))
        return False, False, False, "Invalid config"

    try:
        view = config.get_view(view_name)
    except:
        return False, False, False, "Invalid view"

    zone = get_zone(config.get_id(),zone_name,view_name)
    if zone is False:
        return False, False, False, "Invalid zone"

    return config, view, zone, ""


def does_ip_exist(ip, config, duplicate_record_check=False, create=False):
    try:
        exists = config.get_ip4_address(ip)
    except:
        if create == False:
            return False
        exists = False
    if exists is not False and duplicate_record_check:
        associated_records = exists.get_linked_entities("HostRecord")
        for record in associated_records:
            return False
    if exists is False and create:
        try:
            config.assign_ip4_address(ip, "", "", "MAKE_STATIC")
        except:
            return False

    return True


def split_fqdn(fqdn):
    record = fqdn.split(".", 1)[0]
    zone_name = fqdn.split(".", 1)[1]
    return record, zone_name


def get_key(json, key):
    if key in json:
        return json[key]
    else:
        return None

def get_zone(config, zone_name, view):
    try:
        configuration = g.user.get_api().get_entity_by_id(config)
    except exceptions as e:
        app.logger.error(str(e))
        return False
    zone = find_zone_by_absolute_name(configuration, zone_name, view)

    if (zone is False):
        return False
    return zone

def find_zone_by_absolute_name(config, name, view):
    try:
        search_result = g.user.get_api()._api_client.service.getZonesByHint(config.get_id(), 0, 10, "hint=" + name)
        zones = [g.user.get_api().instantiate_entity(e) for e in search_result.item]
        for zone in zones:
            if (zone.get_property("absoluteName") == name and zone.get_parent_of_type("View").get_name() == view):
                match_zone = zone
    except (BAMException, PortalException, Exception) as e:
        app.logger.error(e.message)
        return False
    if 'match_zone' in locals():
        return match_zone
    return False

def no_data():
    return jsonify({"data": {}, "status":"FAIL", "message":"No data sent"})

def get_json(r):
    try:
        json = r.get_json()
    except:
        json = None
    return json