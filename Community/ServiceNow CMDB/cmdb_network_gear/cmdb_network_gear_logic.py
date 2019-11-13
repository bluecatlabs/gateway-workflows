
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
                        {'title': 'Device Class'},
                        {'title': 'Partition vlans?'},
                        {'title': 'Warranty Expiration'},
                        {'title': 'Asset Tag'},
                        {'title': 'Install Status'}

                        ],
            'data': []}



    # HTTP request
    headers = {"Accept": "application/json"}
    cmdb_url = cmdb_config.servicenow_url + '/api/now/table/cmdb_ci_netgear?sysparm_limit=' + cmdb_config.servicenow_max_query_results
    response = requests.get(cmdb_url, auth=(cmdb_config.servicenow_username, get_password_from_file(cmdb_config.servicenow_secret_file)), headers=headers, verify=False)

    # Get a dict of all manufactures
    manu_dict = {}
    manu_dict = get_all_core_company_manufactures()

    # Check for HTTP codes other than 200
    if response.status_code == 200:
        net_gears = response.json()

        for net_gear in net_gears['result']:
            gear_name = net_gear['name']
            gear_ip = net_gear['ip_address']
            gear_serial = net_gear['serial_number']
            device_type = net_gear['device_type']
            can_partitionvlans = net_gear['can_partitionvlans']
            warranty_expiration = net_gear['warranty_expiration']
            asset_tag = net_gear['asset_tag']

            if net_gear['install_status'] == '114':
                install_status = 'Active'
            elif net_gear['install_status'] == '6':
                install_status = 'In Stock'
            elif net_gear['install_status'] == '7':
                install_status = 'Retired'
            elif net_gear['install_status'] == '106':
                install_status = 'Lab'
            elif net_gear['install_status'] == '101':
                install_status = 'Active'
            else:
                install_status = net_gear['install_status']

            if net_gear['manufacturer']:
                gear_manufacturer = manu_dict[net_gear['manufacturer']['value']]

            if gear_manufacturer == 'Palo Alto':
                device_class = 'Firewall'
            elif gear_manufacturer == 'Silver Peak':
                device_class = 'SDWAN'
            elif "rtr" in gear_name == 'True':
                device_class = 'Router'
            elif "RTR" in gear_name == 'True':
                device_class = 'Router'
            elif "gw" in gear_name == 'True':
                device_class = 'Router'
            elif "GW" in gear_name == 'True':
                device_class = 'Router'
            else:
                device_class = net_gear['device_type']

            data['data'].append([gear_name, gear_ip, gear_serial, gear_manufacturer, device_class, can_partitionvlans, warranty_expiration, asset_tag, install_status])

    return data


def get_all_core_company_manufactures():
    headers = {"Accept": "application/json"}
    cmdb_url = cmdb_config.servicenow_url + '/api/now/table/core_company'
    response = requests.get(cmdb_url, auth=(cmdb_config.servicenow_username, get_password_from_file(cmdb_config.servicenow_secret_file)), headers=headers, verify=False)

    manu_dict = {}

    if response.status_code == 200:
        manufactures = response.json()

        for manufacture in manufactures['result']:
            manu_dict.update({manufacture['sys_id']: manufacture['name']})

    return manu_dict
