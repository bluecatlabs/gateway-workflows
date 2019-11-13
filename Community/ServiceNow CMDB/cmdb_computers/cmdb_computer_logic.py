
"""
Component logic
"""
from bluecat.util import get_password_from_file
from ..cmdb_configuration import cmdb_config
import requests


def raw_table_data(*args, **kwargs):
    # pylint: disable=redefined-outer-name
    data = {'columns': [{'title': 'Name'},
                        {'title': 'Manufacturer'},
                        {'title': 'IP Address'},
                        {'title': 'Serial Number'},
                        {'title': 'MAC Address'},
                        {'title': 'Warranty Expiration'},
                        {'title': 'Assets Tag'},
                        {'title': 'OS'},
                        {'title': 'OS Version'},
                        {'title': 'Serial Number'},
                        {'title': 'Purchase Date'},

                        ],
            'data': []}

    # HTTP request
    headers = {"Accept": "application/json"}
    cmdb_url = cmdb_config.servicenow_url + '/api/now/table/cmdb_ci_computer'
    response = requests.get(cmdb_url, auth=(cmdb_config.servicenow_username, get_password_from_file(cmdb_config.servicenow_secret_file)), headers=headers, verify=False)

    manu_dict = {}
    manu_dict = get_all_core_company_manufactures()

    # Check for HTTP codes other than 200
    if response.status_code == 200:
        computers = response.json()

        for computer in computers['result']:
            computer_name = computer['name']
            computer_ip = computer['ip_address']
            computer_serial = computer['serial_number']
            computer_purchase_date = computer['purchase_date']
            computer_mac = computer['mac_address']
            warranty_expiration = computer['warranty_expiration']
            asset_tag = computer['asset_tag']
            os = computer['os']
            os_version = computer['os_version']
            serial_number = computer['serial_number']

            if computer['manufacturer']:
                # Decode the value of the computer_manufacturer
                computer_manufacturer = manu_dict[computer['manufacturer']['value']]

            data['data'].append([computer_name, computer_manufacturer, computer_ip, computer_serial, computer_mac, warranty_expiration, asset_tag, os, os_version, serial_number, computer_purchase_date])

    return data


def get_computer_manufacturer(link):
    headers = {"Accept": "application/json"}
    response = requests.get(link, auth=(cmdb_config.servicenow_username, get_password_from_file(cmdb_config.servicenow_secret_file)), headers=headers, verify=False)
    manufacturer = response.json()
    return manufacturer['result']['name']


def get_computer_location(link):
    headers = {"Accept": "application/json"}
    response = requests.get(link, auth=(cmdb_config.servicenow_username, get_password_from_file(cmdb_config.servicenow_secret_file)), headers=headers, verify=False)
    location = response.json()
    return location['result']['name']


def get_computer_assets(link):
    headers = {"Accept": "application/json"}
    response = requests.get(link, auth=(cmdb_config.servicenow_username, get_password_from_file(cmdb_config.servicenow_secret_file)), headers=headers, verify=False)
    location = response.json()
    return location


def get_all_core_company_manufactures():
    headers = {"Accept": "application/json"}
    cmdb_url = cmdb_config.servicenow_url + '/api/now/table/core_company?manufacturer=true'
    response = requests.get(cmdb_url, auth=(cmdb_config.servicenow_username, get_password_from_file(cmdb_config.servicenow_secret_file)), headers=headers, verify=False)

    manu_dict = {}

    if response.status_code == 200:
        manufactures = response.json()

        for manufacture in manufactures['result']:
            manu_dict.update({manufacture['sys_id']: manufacture['name']})

    return manu_dict

