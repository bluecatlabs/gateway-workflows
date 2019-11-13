
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
                        {'title': 'Firmware Version'},
                        {'title': 'Ports'},
                        {'title': 'Serial Number'},
                        {'title': 'Manufacturer'},
                        {'title': 'Location'},
                        ],
            'data': []}

    # HTTP request
    headers = {"Accept": "application/json"}
    cmdb_url = cmdb_config.servicenow_url + '/api/now/table/cmdb_ci_ip_router'
    response = requests.get(cmdb_url, auth=(cmdb_config.servicenow_username, get_password_from_file(cmdb_config.servicenow_secret_file)), headers=headers, verify=False)

    # Check for HTTP codes other than 200
    if response.status_code == 200:
        routers = response.json()

        for router in routers['result']:
            router_name = router['name']
            router_ip = router['ip_address']
            router_serial = router['serial_number']
            firmware_version = router['firmware_version']
            ports = router['ports']

            if router['manufacturer']:
                router_manufacturer = get_router_manufacturer(router['manufacturer']['link'])

            if router['location']:
                router_location = get_router_location(router['location']['link'])

            data['data'].append([router_name, router_ip, firmware_version, ports, router_serial, router_manufacturer, router_location])

    return data


def get_router_manufacturer(link):
    headers = {"Accept": "application/json"}
    response = requests.get(link, auth=(cmdb_config.servicenow_username, get_password_from_file(cmdb_config.servicenow_secret_file)), headers=headers, verify=False)
    manufacturer = response.json()
    return manufacturer['result']['name']


def get_router_location(link):
    headers = {"Accept": "application/json"}
    response = requests.get(link, auth=(cmdb_config.servicenow_username, get_password_from_file(cmdb_config.servicenow_secret_file)), headers=headers, verify=False)
    location = response.json()
    return location['result']['name']