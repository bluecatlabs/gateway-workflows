# Copyright 2017 BlueCat Networks (USA) Inc. and its affiliates
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
# Date: 05-12-17
# Gateway Version: 17.10.1
# Description: Example Gateway workflows

from wtforms import SubmitField
from bluecat.wtform_fields import Configuration, IP4Address, CustomStringField, get_ip4_address_endpoint, PlainHTML
from bluecat.wtform_extensions import GatewayForm


def filter_allocated(res):
    if res['status'] == 'SUCCESS' and res['data']['state'] == u'UNALLOCATED':
        res['status'] = 'FAIL'
        res['message'] = 'IP status must be unallocated.'
    return res


class GenericFormTemplate(GatewayForm):
    # When updating the form, remember to make the corresponding changes to the workflow pages
    workflow_name = 'update_ip4_address_example'
    workflow_permission = 'update_ip4_address_example_page'
    configuration = Configuration(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Configuration',
        required=True,
        coerce=int,
        validators=[],
        is_disabled_on_start=False,
        enable_on_complete=['ip4_address']
    )

    ip4_address = IP4Address(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Address',
        required=True,
        inputs={'configuration': 'configuration', 'address': 'ip4_address'},
        on_change=['server_output_ip4_address'],
        server_outputs={'state': 'address_state', 'mac_address': 'mac_address', 'name': 'description'},
        server_side_output_method=get_ip4_address_endpoint,
        result_decorator=filter_allocated,
        enable_on_complete = ['address_state', 'mac_address', 'description', 'submit']
    )

    line_break = PlainHTML('<hr>')

    address_state = CustomStringField(
        label='Address State',
        readonly=True
    )

    mac_address = CustomStringField(label='MAC Address')

    description = CustomStringField(label='Description')

    submit = SubmitField(label='Update')
