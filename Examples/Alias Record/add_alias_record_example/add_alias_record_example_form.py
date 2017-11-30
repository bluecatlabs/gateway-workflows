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

from wtforms import SubmitField
from bluecat.wtform_fields import Configuration, View, Zone, CustomStringField
from bluecat.wtform_extensions import GatewayForm


class GenericFormTemplate(GatewayForm):
    # When updating the form, remember to make the corresponding changes to the workflow pages
    workflow_name = 'add_alias_record_example'
    workflow_permission = 'add_alias_record_example_page'
    configuration = Configuration(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Configuration',
        required=True,
        coerce=int,
        validators=[],
        is_disabled_on_start=False,
        on_complete=['call_view'],
        enable_on_complete=['view']
    )

    view = View(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='View',
        required=True,
        one_off=True,
        on_complete=['call_zone', 'call_linked_record_zone'],
        enable_on_complete=['zone', 'linked_record_zone', 'submit']
    )

    zone = Zone(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Alias Zone',
        required=True,
        clear_below_on_change=False,
        enable_on_complete=['name']
    )

    name = CustomStringField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Name',
        required=True
    )

    linked_record_zone = Zone(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Linked Record Zone',
        required=True,
        clear_below_on_change=False,
        enable_on_complete=['host_record']
    )

    host_record = CustomStringField(
        label='Linked Record',
        required=True
    )

    submit = SubmitField(label='Submit')
