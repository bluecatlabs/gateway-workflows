# Copyright 2020 BlueCat Networks. All rights reserved.

from flask import request, g, jsonify
import os
import subprocess
import csv
from subprocess import CalledProcessError
from werkzeug.utils import secure_filename

from bluecat import route, util
from main_app import app
from bluecat.api_exception import APIException, BAMException, PortalException
from .manage_records_config import DEFAULT_CONFIG_NAME, DEFAULT_VIEW_NAME, DEFAULT_VIEW_ID


#
# GET, PUT or POST
#
@route(app, '/manage_records/endpoint', methods=['GET', 'PUT', 'POST'])
@util.rest_workflow_permission_required('manage_records')
@util.rest_exception_catcher
def manage_records_endpoint():
    # are we authenticated?
    g.user.logger.info('SUCCESS')
    return jsonify({"message": 'The manage_records service is running'}), 200


@route(app, '/manage_records/create_record', methods=['POST'])
@util.rest_workflow_permission_required('manage_records')
@util.rest_exception_catcher
def create_record_endpoint():
    json_data = request.get_json()
    response_data = {'message': ''}

    response_code, response_message = check_common(json_data)
    record_type = json_data['record_type'].strip()

    if (record_type == 'A' or record_type == 'AAAA') and ('ip' not in json_data or json_data['ip'] == '')\
            and ('state' not in json_data or json_data['ip'] == ''):
        response_code = 400
        response_message = 'A or AAAA record, ip not provided'
    if record_type == 'CNAME' and ('linked_record' not in json_data or json_data['linked_record'] == ''):
        response_code = 400
        response_message = 'CNAME record requested, linked_record not provided'
    if record_type == 'TXT' and ('text' not in json_data or json_data['text'] == ''):
        response_code = 400
        response_message = 'TXT record requested, txt not provided'
    if record_type == 'MX' and ('priority' not in json_data or json_data['priority'] == '') and \
            ('linked_record' not in json_data or json_data['linked_record'] == ''):
        response_code = 400
        response_message = 'CNAME record requested, priority or linked_record not provided'
    if record_type == 'TLSA' and ('data' not in json_data or json_data['data'] == ''):
        response_code = 400
        response_message = 'CNAME record requested, data not provided'

    if 'deploy' not in json_data:
        should_deploy = False
    else:
        should_deploy = True
    if 'ping_check' not in json_data:
        should_ping = False
    else:
        should_ping = True

    if response_code == 200:
        try:
            response_code, response_message, response_data, should_deploy, ids = \
                create_record(record_type, json_data, response_data, response_code, should_deploy, should_ping)

            if should_deploy:
                response_code, deploy_message = deploy(ids)
                response_data['deploy_info'] = deploy_message

        except (APIException, BAMException, PortalException) as e:
            response_code = 500
            response_message = 'Unable to create the record %s.%s, exception: %s' %\
                               (json_data['name'].strip(), json_data['zone'].strip(), util.safe_str(e))

    g.user.logger.info(
        'create_record returned with the following message: %s' % response_message)
    response_data['message'] = response_message
    return jsonify(response_data), response_code


def create_record(record_type, record_json, response_data, response_code, should_deploy, should_ping):
    ids = []

    view = g.user.get_api().get_entity_by_id(DEFAULT_VIEW_ID)
    # view = configuration.get_view(DEFAULT_VIEW_NAME)
    absolute_name = '%s.%s' % (record_json['name'].strip(), record_json['zone'].strip())

    if record_type == 'A' or record_type == 'AAAA':
        if record_type == 'A' and (should_ping and ping_check(record_json['ip'].strip(), record_type)):
            response_code = 500
            response_message = 'Detected something at the destination IP(%s), aborting create' % record_json['ip'].strip()
            should_deploy = False
        else:
            new_host = view.add_host_record(absolute_name, [record_json['ip'].strip()])

            response_data['ip'] = new_host.get_addresses()
            response_data['fqdn'] = new_host.get_full_name()
            response_data['fqdn_id'] = new_host.get_id()
            ids.append(new_host.get_id())
            response_message = 'Successfully created record %s, %s(%s)' % \
                               (record_type, absolute_name, record_json['ip'].strip())
    elif record_type == 'CNAME':
        new_alias = view.add_alias_record(absolute_name, record_json['linked_record'].strip())
        response_data['fqdn'] = new_alias.get_full_name()
        response_data['fqdn_id'] = new_alias.get_id()
        ids.append(new_alias.get_id())
        response_message = 'Successfully created record %s, %s, with linked host: %s' % \
                           (record_type, absolute_name, record_json['linked_record'].strip())
    elif record_type == 'TXT':
        new_text = view.add_text_record(absolute_name, record_json['text'].strip())
        response_data['fqdn'] = new_text.get_name()
        response_data['fqdn_id'] = new_text.get_id()
        ids.append(new_text.get_id())
        response_message = 'Successfully created record %s, %s' % \
                           (record_type, absolute_name)
    elif record_type == 'MX':
        new_mx = view.add_mx_record(absolute_name, record_json['priority'].strip(),
                                    record_json['linked_record'].strip())
        response_data['fqdn'] = new_mx.get_name()
        response_data['fqdn_id'] = new_mx.get_id()
        ids.append(new_mx.get_id())
        response_message = 'Successfully created record %s, %s, with linked host: %s' % \
                           (record_type, absolute_name, record_json['linked_record'].strip())
    elif record_type == 'TLSA':
        new_tlsa = view.add_generic_record(absolute_name, 'TLSA', record_json['data'])
        response_data['fqdn'] = new_tlsa.get_name()
        response_data['fqdn_id'] = new_tlsa.get_id()
        ids.append(new_tlsa.get_id())
        response_message = 'Successfully created record %s, %s' % (record_type, absolute_name)
    else:
        response_message = 'Invalid record type submitted'
        response_code = 400
        should_deploy = False

    return response_code, response_message, response_data, should_deploy, ids


@route(app, '/manage_records/delete_record', methods=['POST'])
@util.rest_workflow_permission_required('manage_records')
@util.rest_exception_catcher
def delete_record_endpoint():
    json_data = request.get_json()
    response_data = {'message': ''}

    response_code, response_message = check_common(json_data)
    if 'deploy' not in json_data:
        should_deploy = True
    else:
        should_deploy = False

    if response_code == 200:
        record_type = json_data['record_type'].strip()
        try:
            response_code, response_message, should_deploy, ids = \
                delete_record(record_type, json_data, response_code, should_deploy)

            if should_deploy:
                response_code, deploy_message = deploy(ids)
                response_data['deploy_info'] = deploy_message

        except (APIException, BAMException, PortalException) as e:
            response_code = 500
            response_message = 'Unable to delete the record %s, exception: %s' % \
                               (json_data['record_name'].strip(), util.safe_str(e))

    g.user.logger.info(
        'delete_record returned with the following message: %s' % response_message)
    response_data['message'] = response_message
    return jsonify(response_data), response_code


def delete_record(record_type, record_data, response_code, should_deploy):
    ids = []
    response_message = ''

    configuration = g.user.get_api().get_configuration(DEFAULT_CONFIG_NAME)
    absolute_name = '%s.%s' % (record_data['name'].strip(), record_data['zone'].strip())

    if record_type == 'A' or record_type == 'AAAA':
        found_hosts = g.user.get_api().get_by_object_types(record_data['name'].strip(), 'HostRecord')
        for host in found_hosts:
            if host.get_property('absoluteName') == absolute_name:
                ips = host.get_property('addresses').split(',')
                ids.append(host.get_id())
                host.delete()
        if ips:
            for ip in ips:
                if ':' in ip:
                    ip_address = configuration.get_ip6_address(ip)
                else:
                    ip_address = configuration.get_ip4_address(ip)
                linked_entities = ip_address.get_linked_entities('HostRecord')
                if len(list(linked_entities)) == 0:
                    ip_address.delete()
        response_message = 'Successfully deleted record %s, %s' % (record_type, absolute_name)
    elif record_type == 'CNAME':
        found_alias = g.user.get_api().get_by_object_types(record_data['name'].strip(), 'AliasRecord')
        for alias in found_alias:
            if alias.get_property('absoluteName') == absolute_name:
                ids.append(alias.get_id())
                alias.delete()
                response_message = 'Successfully deleted record %s, %s' % (record_type, absolute_name)
    elif record_type == 'TXT':
        found_txts = g.user.get_api().get_by_object_types(record_data['name'].strip(), 'TXTRecord')
        for txt in found_txts:
            if txt.get_property('absoluteName') == absolute_name:
                ids.append(txt.get_id())
                txt.delete()
        response_message = 'Successfully deleted record %s, %s' % (record_type, absolute_name)
    elif record_type == 'MX':
        found_mxs = g.user.get_api().get_by_object_types(record_data['name'].strip(), 'MXRecord')
        for mx in found_mxs:
            if mx.get_property('absoluteName') == absolute_name:
                ids.append(mx.get_id())
                mx.delete()
        response_message = 'Successfully deleted record %s, %s' % (record_type, absolute_name)
    elif record_type == 'TLSA':
        found_tlsas = g.user.get_api().get_by_object_types(record_data['name'].strip(), 'GenericRecord')
        for tlsa in found_tlsas:
            if tlsa.get_property('absoluteName') == absolute_name:
                ids.append(tlsa.get_id())
                tlsa.delete()
        response_message = 'Successfully deleted record %s, %s' % (record_type, absolute_name)
    else:
        response_message = 'Invalid record type submitted'
        response_code = 400
        should_deploy = False

    return response_code, response_message, should_deploy, ids



@route(app, '/manage_records/update_record', methods=['POST'])
@util.rest_workflow_permission_required('manage_records')
@util.rest_exception_catcher
def update_record_endpoint():
    json_data = request.get_json()
    response_data = {'message': ''}

    response_code, response_message = check_common(json_data)
    record_type = json_data['record_type'].strip()

    if (record_type == 'A' or record_type == 'AAAA') and ('ip' not in json_data or json_data['ip'] == ''):
        response_code = 400
        response_message = 'A or AAAA record, ip not provided'
    if record_type == 'CNAME' and ('linked_record' not in json_data or json_data['linked_record'] == ''):
        response_code = 400
        response_message = 'CNAME record requested, linked_record not provided'
    if record_type == 'TXT' and ('text' not in json_data or json_data['text'] == ''):
        response_code = 400
        response_message = 'TXT record requested, txt not provided'
    if record_type == 'MX' and ('priority' not in json_data or json_data['priority'] == '') and \
            ('linked_record' not in json_data or json_data['linked_record'] == ''):
        response_code = 400
        response_message = 'CNAME record requested, priority or linked_record not provided'
    if record_type == 'TLSA' and ('data' not in json_data or json_data['data'] == ''):
        response_code = 400
        response_message = 'CNAME record requested, data not provided'

    if 'deploy' not in json_data:
        should_deploy = False
    else:
        should_deploy = True
    if 'ping_check' not in json_data:
        should_ping = False
    else:
        should_ping = True

    if response_code == 200:
        try:
            response_code, response_message, response_data, should_deploy, ids = \
                update_record(record_type, json_data, response_data, should_deploy, should_ping)
            if should_deploy:
                response_code, deploy_message = deploy(ids)
                response_data['deploy_info'] = deploy_message

        except (APIException, BAMException, PortalException) as e:
            response_code = 500
            response_message = 'Unable to create the record %s.%s, exception: %s' %\
                               (json_data['name'].strip(), json_data['zone'].strip(), util.safe_str(e))

    g.user.logger.info(
        'create_record returned with the following message: %s' % response_message)
    response_data['message'] = response_message
    return jsonify(response_data), response_code


def update_record(record_type, record_data, response_data, should_deploy, should_ping):
    ids = []
    response_code = 200
    configuration = g.user.get_api().get_configuration(DEFAULT_CONFIG_NAME)
    view = g.user.get_api().get_entity_by_id(DEFAULT_VIEW_ID)
    # view = configuration.get_view(DEFAULT_VIEW_NAME)
    absolute_name = '%s.%s' % (record_data['name'].strip(), record_data['zone'].strip())

    if record_type == 'A' or record_type == 'AAAA':
        if record_type == 'A' and (should_ping and ping_check(record_data['ip'].strip(), record_type)):
            response_code = 500
            response_message = 'Detected something at the destination IP(%s), aborting update' % record_data['ip'].strip()
            should_deploy = False
        else:
            found_hosts = g.user.get_api().get_by_object_types(record_data['name'].strip(), 'HostRecord')

            for host in found_hosts:
                if host.get_property('absoluteName') == absolute_name:
                    ips = host.get_property('addresses').split(',')
                    ids.append(host.get_id())
                    host.set_addresses([record_data['ip'].strip()])
                    host.update()

                    response_data['addresses'] = host.get_addresses()
                    response_data['fqdn'] = host.get_full_name()
                    response_data['fqdn_id'] = host.get_id()
                    break
            if ips:
                for ip in ips:
                    if ':' in ip:
                        ip_address = configuration.get_ip6_address(ip)
                    else:
                        ip_address = configuration.get_ip4_address(ip)
                    linked_entities = ip_address.get_linked_entities('HostRecord')
                    if len(list(linked_entities)) == 0:
                        ip_address.delete()
            response_message = 'Successfully updated record %s, %s(%s)' % \
                               (record_type, absolute_name, record_data['ip'].strip())
    elif record_type == 'CNAME':
        found_alias = g.user.get_api().get_by_object_types(record_data['name'].strip(), 'AliasRecord')
        for alias in found_alias:
            if alias.get_property('absoluteName') == absolute_name:
                ids.append(alias.get_id())
                alias.set_property('linkedRecordName', record_data['linked_record'].strip())
                response_data['fqdn'] = alias.get_full_name()
                response_data['fqdn_id'] = alias.get_id()
                alias.update()
                break
        response_message = 'Successfully updated record %s, %s, with new linked host: %s' %\
                           (record_type, absolute_name, record_data['linked_record'].strip())
    elif record_type == 'TXT':
        found_txts = g.user.get_api().get_by_object_types(record_data['name'].strip(), 'TXTRecord')
        for txt in found_txts:
            if txt.get_property('absoluteName') == absolute_name:
                ids.append(txt.get_id())
                txt.set_property('txt', record_data['text'].strip())
                response_data['fqdn'] = txt.get_name()
                response_data['fqdn_id'] = txt.get_id()
                txt.update()
                break
        response_message = 'Successfully updated record %s, %s' %\
                           (record_type, absolute_name)
    elif record_type == 'MX':
        found_mxs = g.user.get_api().get_by_object_types(record_data['name'].strip(), 'MXRecord')
        for mx in found_mxs:
            if mx.get_property('absoluteName') == absolute_name:
                ids.append(mx.get_id())
                response_data['fqdn'] = mx.get_name()
                response_data['fqdn_id'] = mx.get_id()
                mx.set_property('linkedRecordName', record_data['linked_record'].strip())
                mx.set_property('priority', record_data['priority'].strip())
                mx.update()
                break
        response_message = 'Successfully updated record %s, %s, with linked host: %s' %\
                           (record_type, absolute_name, record_data['linked_record'].strip())
    elif record_type == 'TLSA':
        found_tlsas = g.user.get_api().get_by_object_types(record_data['name'].strip(), 'GenericRecord')
        for tlsa in found_tlsas:
            if tlsa.get_property('absoluteName') == absolute_name:
                ids.append(tlsa.get_id())
                response_data['fqdn'] = tlsa.get_name()
                response_data['fqdn_id'] = tlsa.get_id()
                tlsa.set_property('rdata', record_data['data'])
                tlsa.update()
        new_tlsa = view.add_generic_record(absolute_name, 'TLSA', record_data['data'])
        ids.append(new_tlsa.get_id())
        response_message = 'Successfully updated record %s, %s' % (record_type, absolute_name)
    else:
        response_message = 'Invalid record type submitted'
        response_code = 400
        should_deploy = False

    return response_code, response_message, response_data, should_deploy, ids


@route(app, '/manage_records/bulk_process', methods=['POST'])
@util.rest_workflow_permission_required('manage_records')
@util.rest_exception_catcher
def bulk_process_endpoint():
    # Actions - C,U,D
    # A - record_type,action,deploy,name,zone,ip
    # AAAA - record_type,action,deploy,name,zone,ip
    # CNAME - record_type,action,deploy,name,zone,linked_record
    # TXT - record_type,action,deploy,name,zone,text
    # MX - record_type,action,deploy,name,zone,linked_record
    # TLSA - record_type,action,deploy,name,zone,data
    response_code = 200
    response_data = {'message': ''}
    ids = []

    submitted_file = request.files['file']
    if submitted_file.filename is None or submitted_file.filename == '':
        response_message = 'No file submitted'
        response_code = 400
    elif is_csv(submitted_file.filename):
        try:
            filename = os.path.join('bluecat_portal/uploads', secure_filename(submitted_file.filename))
            submitted_file.save(filename)

            file_reader = csv.reader(open(filename, 'rU'))

            for line in file_reader:
                line_data = {}
                info = {'name': line[3].strip(),
                        'zone': line[4].strip()
                        }
                should_deploy = line[2]
                key_name = '%s-%s-%s.%s' % (line[0], line[1], line[3].strip(), line[4].strip())

                if line[1] == 'C' or line[1] == 'U':
                    if line[0] == 'A' or line[0] == 'AAAA':
                        info['ip'] = line[5].strip()
                    elif line[0] == 'CNAME':
                        info['linked_record'] = line[5].strip()
                    elif line[0] == 'TXT':
                        info['text'] = line[5]
                    elif line[0] == 'MX':
                        info['linked_record'] = line[5].strip()
                        info['priority'] = line[6].strip()
                    elif line[0] == 'TLSA':
                        info['data'] = line[5]

                try:
                    if line[1] == 'C':
                        response_code, response_message, line_data, should_deploy, ids = \
                            create_record(line[0], info, line_data, response_code, should_deploy)
                        line_message = 'Completed create with the following message: %s' % response_message
                    elif line[1] == 'D':
                        response_code, response_message, should_deploy, ids = \
                            delete_record(line[0], info, response_code, should_deploy)
                        line_message = 'Completed delete with the following message: %s' % response_message
                    elif line[1] == 'U':
                        response_code, response_message, line_data, should_deploy, ids = \
                            update_record(line[0], info, line_data, should_deploy)
                        line_message = 'Completed update with the following message: %s' % response_message
                    else:
                        line_message = 'Invalid operation submitted: %s, skipping line' % line[1]

                    if should_deploy == 'True':
                        response_code, deploy_message = deploy(ids)
                        line_data['deploy_info'] = deploy_message

                except (APIException, BAMException, PortalException) as e:
                    line_message = 'Encountered an error while processing line: %s' % util.safe_str(e)

                response_data[key_name] = {'line_message': line_message,
                                           'line_data': line_data}

        except Exception as e:
            response_code = 500
            response_message = 'Encountered an error while processing the file, stopped processing: %s' % util.safe_str(e)
        else:
            os.remove(os.path.join('bluecat_portal/uploads', secure_filename(submitted_file.filename)))
            response_message = 'Successfully processed bulk file: %s' % submitted_file.filename
    else:
        response_message = 'Invalid file submitted. Either not a csv or doesn\'t exist, %s' % submitted_file.filename
        response_code = 400

    g.user.logger.info('bulk_create completed with the following message: %s' % response_message)
    response_data['message'] = response_message
    return jsonify(response_data), response_code


@route(app, '/manage_records/deploy_records', methods=['POST'])
@util.rest_workflow_permission_required('manage_records')
@util.rest_exception_catcher
def deploy_records_endpoint():
    json_data = request.get_json()
    response_code = 200
    response_message = ''
    response_data = {'message': ''}

    # A list of FQDN IDs should be submitted for deployment. These IDs are the same one from the provision_server API
    if 'ids' not in json_data:
        response_code = 400
        response_message = 'ids not provided'

    if response_code == 200:
        id_list = []
        for ip in json_data['ids']:
            id_list.append(ip)

        response_code, response_message = deploy(id_list)

    g.user.logger.info(
        'deploy_records completed with the following message: %s' % response_message)
    response_data['message'] = response_message
    return jsonify(response_data), response_code


def deploy(ids):
    try:
        # API call to run the selective deployment
        deploy_return = g.user.get_api().selective_deploy_synchronous(ids, properties='scope=related', timeout=30)
        return 200, deploy_return
    except (APIException, BAMException, PortalException) as e:
        return 500, 'Unable to deploy the records, exception: %s' % util.safe_str(e)


@route(app, '/manage_records/get_record', methods=['POST'])
@util.rest_workflow_permission_required('manage_records')
@util.rest_exception_catcher
def get_record_endpoint():
    json_data = request.get_json()
    response_data = {'message': ''}

    response_code, response_message = check_common(json_data)

    if response_code == 200:
        record_type = json_data['record_type'].strip()

        try:
            absolute_name = '%s.%s' % (json_data['name'].strip(), json_data['zone'].strip())

            if record_type == 'A' or record_type == 'AAAA':
                found_hosts = g.user.get_api().get_by_object_types(json_data['name'].strip(), 'HostRecord')
                for host in found_hosts:
                    if host.get_property('absoluteName') == absolute_name:
                        response_data['id'] = host.get_id()
                        response_data['addresses'] = host.get_addresses()
                        break
                response_message = 'Found record %s, %s' % (record_type, absolute_name)
            elif record_type == 'CNAME':
                found_alias = g.user.get_api().get_by_object_types(json_data['name'].strip(), 'AliasRecord')
                for alias in found_alias:
                    if alias.get_property('absoluteName') == absolute_name:
                        response_data['id'] = alias.get_id()
                        response_data['linked_record'] = alias.get_property('linkedRecordName')
                        break
                response_message = 'Found record %s, %s' % (record_type, absolute_name)
            elif record_type == 'TXT':
                found_txts = g.user.get_api().get_by_object_types(json_data['name'].strip(), 'TXTRecord')
                for txt in found_txts:
                    if txt.get_property('absoluteName') == absolute_name:
                        response_data['id'] = txt.get_id()
                        response_data['text'] = txt.get_property('txt')
                        break
                response_message = 'Found record %s, %s' % (record_type, absolute_name)
            elif record_type == 'MX':
                found_mxs = g.user.get_api().get_by_object_types(json_data['name'].strip(), 'MXRecord')
                for mx in found_mxs:
                    if mx.get_property('absoluteName') == absolute_name:
                        response_data['id'] = mx.get_id()
                        response_data['priority'] = mx.get_property('priority')
                        response_data['linked_record'] = mx.get_property('linkedRecordName')
                        break
                response_message = 'Found record %s, %s' % (record_type, absolute_name)
            elif record_type == 'TLSA':
                found_tlsas = g.user.get_api().get_by_object_types(json_data['name'].strip(), 'GenericRecord')
                for tlsa in found_tlsas:
                    if tlsa.get_property('absoluteName') == absolute_name:
                        response_data['id'] = tlsa.get_id()
                        response_data['data'] = tlsa.get_property('rdata')
                        break
                response_message = 'Found record %s, %s' % (record_type, absolute_name)
            else:
                response_message = 'Invalid record type submitted'
                response_code = 400
        except (APIException, BAMException, PortalException) as e:
            response_code = 500
            response_message = 'Unable to find the record, exception: %s' % util.safe_str(e)

    g.user.logger.info(
        'get_record completed with the following message: %s' % response_message)
    response_data['message'] = response_message
    return jsonify(response_data), response_code


def check_common(json_data):
    return_code = 200
    response_message = "Fill In Response Message"

    if 'record_type' not in json_data or json_data['record_type'] == '':
        return_code = 400
        response_message = 'record_type not provided'
    if 'name' not in json_data or json_data['name'] == '':
        return_code = 400
        response_message = 'name not provided'
    if 'zone' not in json_data or json_data['zone'] == '':
        return_code = 400
        response_message = 'zone not provided'

    return return_code, response_message


def check_common_reservation(json_data):
    return_code = 200
    response_message = "Fill In Response Message"
    if 'mac' not in json_data or json_data['mac'] == '':
        return_code = 400
        response_message = 'mac not provided'
    if 'ip' not in json_data or json_data['ip'] == '':
        return_code = 400
        response_message = 'ip not provided'

    return return_code, response_message


def ping_check(ip_address, record_type):
    try:
        if record_type == 'A':
            ping_command = 'ping'
        elif record_type == 'AAAA':
            ping_command = 'ping6'
        output = subprocess.check_output([ping_command, ip_address, '-c 1'], stderr=subprocess.STDOUT,
                                         shell=False)
    except CalledProcessError as e:
        if '0 packets received' in str(e.output):
            return False

    return True


def is_csv(filename):
    bits = filename.split('.')
    if len(bits) > 1:
        return bits[-1] == 'csv'
    else:
        return False
