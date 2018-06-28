# Copyright 2018 BlueCat Networks (USA) Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By: BlueCat Networks
# Date: 04-05-18
# Gateway Version: 18.6.1
# Description: Example Gateway workflows


"""
Add static IPv4 address form
"""
from wtforms import SubmitField
from bluecat.wtform_fields import Configuration, View, Zone, IP4Address, CustomStringField
from bluecat.wtform_extensions import GatewayForm


def filter_unallocated(res):
    """
    Filter unallocated IP.

    :param res:
    :return:
    """
    if res['status'] == 'SUCCESS' and res['data']['state'] != 'UNALLOCATED':
        res['status'] = 'FAIL'
        res['message'] = 'IP status must be unallocated.'
    return res


class GenericFormTemplate(GatewayForm):
    """ Form to generate HTML and Javascript for the add_static_ip4_address_example workflow

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'add_static_ip4_address_example'
    workflow_permission = 'add_static_ip4_address_example_page'
    configuration = Configuration(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Configuration',
        required=True,
        coerce=int,
        clear_below_on_change=False,
        is_disabled_on_start=False,
        enable_dependencies={'on_complete': ['ip4_address']},
        disable_dependencies={'on_change': ['ip4_address']},
        clear_dependencies={'on_change': ['ip4_address', 'view', 'mac_address', 'description']}
    )

    ip4_address = IP4Address(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Address',
        required=True,
        inputs={'configuration': 'configuration', 'address': 'ip4_address'},
        result_decorator=filter_unallocated,
        on_complete=['call_view'],
        clear_below_on_change=False,
        should_cascade_disable_on_change=True,
        enable_dependencies={'on_complete': ['view', 'mac_address', 'description', 'submit']},
        disable_dependencies={'on_change': ['view', 'mac_address', 'description', 'submit']},
        display_message=True
    )

    mac_address = CustomStringField(
        label='MAC Address'
    )

    description = CustomStringField(
        label='Description'
    )

    view = View(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='View',
        one_off=True,
        on_complete=['call_zone'],
        clear_below_on_change=False,
        should_cascade_disable_on_change=True,
        should_cascade_clear_on_change=True,
        enable_dependencies={'on_complete': ['zone']},
        disable_dependencies={'on_change': ['zone']},
        clear_dependencies={'on_change': ['zone']}
    )

    zone = Zone(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Zone',
        clear_below_on_change=False,
        should_cascade_disable_on_change=True,
        should_cascade_clear_on_change=True,
        enable_dependencies={'on_complete': ['hostname']},
        disable_dependencies={'on_change': ['hostname']},
        clear_dependencies={'on_change': ['hostname']}
    )

    hostname = CustomStringField(
        label='Hostname'
    )

    submit = SubmitField(label='Submit')
