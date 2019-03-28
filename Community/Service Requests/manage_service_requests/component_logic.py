import requests

from .manage_service_requests_config import ManageServiceRequestsConfig


headers = {"Accept": "application/json"}


def raw_table_data(*args, **kwargs):
    """Returns table formatted data for display in the TableField component"""
    # Declare table column header and data
    data = {'columns': [{'title': 'Ticket'},
                        {'title': 'Host Record'},
                        {'title': 'IP Address'},
                        {'title': 'Creator'},
                        {'title': 'Date Created'},
                        {'title': 'Actions'},
                        ],
            'data': []}

    # HTTP request
    ticket_url = ManageServiceRequestsConfig.servicenow_url + '?assigned_to=admin&state!=closed&active=true'
    response = requests.get(ticket_url, auth=(ManageServiceRequestsConfig.servicenow_username, ManageServiceRequestsConfig.servicenow_password), headers=headers, verify=False)

    # Check for HTTP codes other than 200
    if response.status_code == 200:
        tickets = response.json()
        for ticket in tickets['result']:
            description = ticket['description'].split(',')
            if '|' not in ticket['short_description']:
                data['data'].append([
                    ticket['number'],
                    description[2].partition('host_record=')[2],
                    description[3].partition('ip_address=')[2],
                    'admin',
                    ticket['sys_created_on'],
                    '<button type="button" class="btn btn-primary btn-xs">Approve</button>'
                ])

    return data