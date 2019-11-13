
"""
Component logic
"""
from bluecat.util import get_password_from_file
from ..cmdb_configuration import cmdb_config
import requests


def raw_table_data(*args, **kwargs):
    # pylint: disable=redefined-outer-name
    data = {'columns': [{'title': 'Name'},
                        {'title': 'IP Address'},
                        {'title': 'Serial Number'},
                        {'title': 'Manufacturer'},
                        ],
            'data': []}

    # HTTP request
    headers = {"Accept": "application/json"}
    cmdb_url = cmdb_config.servicenow_url + '/api/now/table/cmdb_ci_ip_switch'
    response = requests.get(cmdb_url, auth=(cmdb_config.servicenow_username, get_password_from_file(cmdb_config.servicenow_secret_file)), headers=headers, verify=False)

    # Check for HTTP codes other than 200
    if response.status_code == 200:
        switches = response.json()

        for switch in switches['result']:
            switch_name = switch['name']
            switch_ip = switch['ip_address']
            switch_serial = switch['serial_number']

            if switch['manufacturer']:
                switch_manufacturer = get_switch_manufacturer(switch['manufacturer']['link'])

            data['data'].append([switch_name, switch_ip, switch_serial, switch_manufacturer])

    return data


def get_switch_manufacturer(link):
    headers = {"Accept": "application/json"}
    response = requests.get(link, auth=(cmdb_config.servicenow_username, get_password_from_file(cmdb_config.servicenow_secret_file)), headers=headers, verify=False)
    manufacturer = response.json()
    return manufacturer['result']['name']
