# Copyright 2019 BlueCat Networks. All rights reserved.
import csv
from io import StringIO

from flask import g
from flask_mail import Mail, Message

from main_app import app
from bluecat import route, util
import config.default_config as config
from .user_inventory_util import response_handler


@route(app, '/user_inventory/user_inventory_endpoint', methods=['GET'])
@util.rest_workflow_permission_required('user_inventory_page')
@util.rest_exception_catcher
def user_inventory_user_inventory_page():
    # Define variables
    csv_file = StringIO()
    csv_writer = csv.writer(csv_file)
    mail = Mail(app)

    # Iterate through users and write properties to buffer
    for user in g.user.get_api().get_by_object_types('*', 'User'):
        # Retrieve access rights for user
        user_rights = []
        for access_right in user.get_access_rights():
            access_object = g.user.get_api().get_entity_by_id(access_right.get_entity_id()).get_name()
            user_rights.append('%s for %s with overrides: %s'
                               % (access_right._api_entity['value'], access_object, access_right._api_entity['overrides']))
        # Write user properties to CSV
        csv_writer.writerow([
            user.get_name(),
            user.get_property('email'),
            user.get_property('userType'),
            user.get_property('userAccessType'),
            ', '.join(user_rights)
        ])

    # Send email with buffer as an attached CSV
    msg = Message(subject=u'User Inventory Report', html='User Inventory Report', recipients=config.ADMINS)
    msg.attach('user_inventory_report.csv', 'text/csv', csv_file.getvalue())
    try:
        mail.send(msg)
    except Exception as e:
        g.user.logger.error('%s' % util.safe_str(e), msg_type=g.user.logger.EXCEPTION)
        return response_handler('Unable to email report with error: %s' % util.safe_str(e), 500)

    return response_handler('Inventory report successfully generated', 200)
