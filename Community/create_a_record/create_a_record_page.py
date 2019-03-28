# Copyright 2018 BlueCat Networks. All rights reserved.
from flask import request, g

from main_app import app
from bluecat import route, util
import config.default_config as config
from bluecat.api_exception import PortalException, BAMException
from .create_a_record_util import response_handler, get_fields, get_configuration_and_view, complete_selective_deploy


@route(app, '/create_a_record/create_a_record_endpoint', methods=['POST'])
@util.rest_workflow_permission_required('create_a_record_page')
@util.rest_exception_catcher
def create_a_record_create_a_record_page():
    # Retrieve request json parameters
    record_name, ip4_address, parent_zone = get_fields(request.get_json())

    # Display message if required parameters are not defined
    if not record_name:
        g.user.logger.error('Record name parameter not defined in json data - use key \'record_name\'')
        return response_handler('Record name parameter not defined in json data - use key \'record_name\'', 400)
    elif not ip4_address:
        g.user.logger.error('IP4 address parameter not defined in json data - use key \'address\'')
        return response_handler('IP4 address parameter not defined in json data - use key \'address\'', 400)
    elif not parent_zone:
        g.user.logger.error('Parent Zone parameter not defined in json data - use key \'parent_zone\'')
        return response_handler('Parent Zone parameter not defined in json data - use key \'parent_zone\'', 400)

    # Retrieve configuration and view
    try:
        configuration, view = get_configuration_and_view(configuration_name=config.default_configuration,
                                                         view_name=config.default_view)
    except PortalException as e:
        g.user.logger.error('%s' % e, msg_type=g.user.logger.EXCEPTION)
        return response_handler('Configuration %s or view %s undefined in BAM' % config.default_configuration, 400)

    # Split addresses by comma in case multiple addresses are being added
    ip4_entity = [address.strip() for address in ip4_address.split(',')]

    # Add host record
    try:
        host_record = view.add_host_record(record_name + '.' + parent_zone, ip4_entity, '-1', 'parentZoneName=%s' % parent_zone)
        g.user.logger.info('Host record %s successfully added with address(es)'
                           ' %s'
                           % (host_record.get_property('absoluteName'), host_record.get_property('addresses')))
    except BAMException as e:
        if 'Duplicate of another item' in util.safe_str(e):
            g.user.logger.warning('Host record %s is a duplicate of an already existing record in BAM' % record_name)
            return response_handler('Host record %s is a duplicate of an already existing record in BAM' % record_name, 500)
        elif 'Could not locate the network' in util.safe_str(e):
            g.user.logger.warning('One or more parent networks are not defined for addresses %s' % ip4_entity)
            return response_handler('One or more parent networks are not defined for addresses %s' % ip4_entity, 500)
        else:
            g.user.logger.error('%s' % e, msg_type=g.user.logger.EXCEPTION)
            return response_handler('Unable to add host record %s with error: %s' % (record_name, util.safe_str(e)), 500)

    # Selective deploy record to DNS master of zone
    try:
        error = complete_selective_deploy(record_id=host_record.get_id())
    except Exception as e:
        g.user.logger.error('%s' % e, msg_type=g.user.logger.EXCEPTION)
        return response_handler('Record %s could not be deployed with error: %s'
                                % (host_record.get_property('absoluteName'), util.safe_str(e)), 500)

    # Check for any errors in selective deploy
    if error:
        return response_handler('Record %s could not be deployed with error: %s'
                                % (host_record.get_property('absoluteName'), error), 500)

    return response_handler('Host Record %s added to zone %s with IP4 address: %s'
                            % (host_record.get_property('absoluteName'), 'ins.dell.com',
                               host_record.get_property('addresses')), 200)
