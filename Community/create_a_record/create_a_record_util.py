from time import sleep

from flask import g, make_response, jsonify

http_code_map = {
    200: 'Ok',
    400: 'Bad Request',
    500: 'Internal Server Error'
}


def get_fields(json):
    """
    Retrieve arguments from JSON request
    :param json: JSON request sent in payload
    :return: Parsed arguments
    """
    record_name = json.get('record_name')
    ip4_address = json.get('address')
    parent_zone = json.get('parent_zone')

    return record_name, ip4_address, parent_zone


def response_handler(description, http_code):
    """
    :param description: Description of response
    :param http_code: HTTP error code
    :return: JSON response to REST endpoint with a status, code and description
    """
    return make_response(jsonify({
        'status': http_code_map[http_code],
        'code': http_code,
        'description': description
    }), http_code)


def get_configuration_and_view(configuration_name, view_name):
    """
    Retrieve configuration and view object
    :param configuration_name: Configuration name of object to return
    :param view_name: View name of object to return
    :return: Configuration and view object
    """
    configuration = g.user.get_api().get_configuration(configuration_name)
    view = configuration.get_view(view_name)
    return configuration, view


def complete_selective_deploy(record_id):
    """
    Selective deploy record to DNS master of zone
    :param record_id: Record ID of object to deploy
    :return: Error string if exists otherwise None
    """
    # Deploy record on BDDS using selective deploy
    deploy_token = g.user.get_api().selective_deploy([record_id], 'scope=related')

    # Periodically check if deployment is finished
    while True:
        deployment_status = g.user.get_api().get_deployment_task_status(deploy_token)
        if deployment_status['status'] == 'QUEUED' or deployment_status['status'] == 'STARTED':
            sleep(1)
        else:
            if deployment_status['response']['errors']:
                g.user.logger.error('Unable to deploy to BDDS with error: %s' % deployment_status['response']['errors'])
                return deployment_status['response']['errors']
            else:
                return None
