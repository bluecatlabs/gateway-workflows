# Copyright 2019 BlueCat Networks. All rights reserved.

# Various Flask framework items.
import os
import sys
import requests
import io
import csv

from flask import url_for, redirect, render_template, flash, g, json, make_response
from datetime import datetime, timedelta

from bluecat import route, util
from bluecat.constants import IPAssignmentActionValues
from bluecat.api_exception import PortalException, BAMException
import config.default_config as config
from main_app import app
from .manage_service_requests_form import GenericFormTemplate
from .manage_service_requests_config import ManageServiceRequestsConfig

headers = {"Accept": "application/json"}


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/manage_service_requests/manage_service_requests_endpoint')
@util.workflow_permission_required('manage_service_requests_page')
@util.exception_catcher
def manage_service_requests_manage_service_requests_page():
    form = GenericFormTemplate()

    return render_template(
        'manage_service_requests_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/manage_service_requests/form', methods=['POST'])
@util.workflow_permission_required('manage_service_requests_page')
@util.exception_catcher
def manage_service_requests_manage_service_requests_page_form():
    form = GenericFormTemplate()

    if form.validate_on_submit():
        # Put form processing code here
        g.user.logger.info('SUCCESS')
        flash('success', 'succeed')
        return redirect(url_for('manage_service_requestsmanage_service_requests_manage_service_requests_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'manage_service_requests_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )


@route(app, '/manage_service_requests/form/<ticket>/<absolute_name>/<address>', methods=['GET', 'POST'])
@util.workflow_permission_required('manage_service_requests_page')
@util.exception_catcher
def approve_ticket(ticket, absolute_name, address):
    ip4_address_list = [address]
    try:
        view = g.user.get_api().get_configuration(config.default_configuration).get_view(config.default_view)
    except PortalException as e:
        g.user.logger.error('%s' % e, msg_type=g.user.logger.EXCEPTION)
        flash('Unable to retrieve configuration or view defined in settings')
        return redirect(url_for('approve_snow_ticket_create_hostapprove_snow_ticket_create_host_approve_snow_ticket_create_host_page'))

    # Adding the ticket number to the comments
    props = {'comments': 'ServiceNow Ticket number: %s' % ticket}

    # Add host Record
    try:
        ip4_address = g.user.get_api().get_configuration(config.default_configuration).get_ip4_address(address)

        ip4_address.change_state_ip4_address(IPAssignmentActionValues.MAKE_STATIC, '')
        host_record = view.add_host_record(absolute_name, ip4_address_list, -1, props)
    except BAMException as e:
        g.user.logger.error('%s' % e, msg_type=g.user.logger.EXCEPTION)
        flash('Unable to add host record with error %s' % util.safe_str(e))
        return redirect(url_for('manage_sservice_requestsmanage_service_requests_manage_service_requests_page'))

    # Setup the date format
    resolved_date = datetime.now() + timedelta(minutes=6)

    ticket_information = {
        'close_code': 'Successful',
        'close_notes': 'Approved',
        'state': '3',
        'assignment_group': 'Team Development Code Reviewers',
        'resolved_date': resolved_date.strftime("%Y-%m-%d %H:%M")
    }

    # get the sys_id of the ticket
    response = requests.get(ManageServiceRequestsConfig.servicenow_url + '?sysparm_query=number=' + ticket,
                            auth=(ManageServiceRequestsConfig.servicenow_username, ManageServiceRequestsConfig.servicenow_password),
                            headers=headers,
                            verify=False)
    if response.status_code == 200:
        returned_values = response.json()
        for r in returned_values['result']:
            ticket_sys_id = r['sys_id']

    requests.put(ManageServiceRequestsConfig.servicenow_url + '/' + ticket_sys_id,
                 auth=(ManageServiceRequestsConfig.servicenow_username, ManageServiceRequestsConfig.servicenow_password),
                 headers=headers,
                 data=json.dumps(ticket_information),
                 verify=False)

    flash('Success - Change Request: ' + ticket + ' Closed and Host: ' + host_record.get_name() + ' created', 'succeed')
    return redirect(url_for('manage_service_requestsmanage_service_requests_manage_service_requests_page'))


@route(app, '/manage_service_requests/generate_service_requests_report', methods=['GET'])
@util.rest_workflow_permission_required('manage_service_requests_page')
@util.rest_exception_catcher
def generate_service_requests_report():
    try:
        string_output = io.StringIO()

        csv_writer = csv.writer(string_output)

        csv_writer.writerow(['TicketNum', 'HostRecord', 'HostID', 'IPAddress', 'IPState', 'IPID', 'RequestCreate',
                             'RequestedBy', 'LastUpdate', 'CloseDate', 'CloseNotes'])
        ticket_url = ManageServiceRequestsConfig.servicenow_url + '?assigned_to=admin'
        response = requests.get(ticket_url, auth=(ManageServiceRequestsConfig.servicenow_username, ManageServiceRequestsConfig.servicenow_password), headers=headers, verify=False)
        data = []
        # Check for HTTP codes other than 200
        if response.status_code == 200:
            tickets = response.json()
            for ticket in tickets['result']:
                if 'BlueCat' in ticket['short_description']:
                    description = ticket['description'].split(',')
                    ip_address = g.user.get_api().get_configuration(config.default_configuration).get_ip4_address(
                        description[3].partition('ip_address=')[2])
                    hosts = ip_address.get_linked_entities('HostRecord')
                    host_id = ''
                    for host in hosts:
                        host_id = host.get_id()
                    info = [
                        ticket['number'],
                        description[2].partition('host_record=')[2],
                        host_id,
                        ip_address.get_address(),
                        ip_address.get_state(),
                        ip_address.get_id(),
                        ticket['sys_created_on'],
                        ticket['sys_created_by'],
                        ticket['sys_updated_on'],
                        ticket['closed_at'],
                        ticket['close_notes']
                    ]

                    csv_writer.writerow(info)

            output_response = make_response(string_output.getvalue())
            output_response.headers['Content-Disposition'] = 'attachment; filename=service_requests.csv'
            output_response.headers['Content-type'] = 'text/csv'
        else:
            raise Exception('Received a non 200 response from the service provider: %s, content: %s'
                            % (response.status_code, response.content))
    except Exception as e:
        return_message = 'Encountered an error while generating the CSV file: %s' % util.safe_str(e)
        output_response = make_response(return_message, 500)

    return output_response
