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
# Date: 2018-09-27
# Gateway Version: 18.10.1
# Description: Example Gateway workflows


"""
Add alias record form
"""
from wtforms import SubmitField
from bluecat.wtform_fields import Configuration, View, Zone, CustomStringField
from bluecat.wtform_extensions import GatewayForm


class GenericFormTemplate(GatewayForm):
    """ Form to generate HTML and Javascript for the add_alias_record_example workflow

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'add_alias_record_example'
    workflow_permission = 'add_alias_record_example_page'
    configuration = Configuration(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Configuration',
        required=True,
        coerce=int,
        is_disabled_on_start=False,
        on_complete=['call_view'],
        enable_dependencies={'on_complete': ['view']},
        disable_dependencies={'on_change': ['view']},
        clear_dependencies={'on_change': ['view']}
    )

    view = View(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='View',
        required=True,
        one_off=True,
        on_complete=['call_zone', 'call_linked_record_zone'],
        enable_dependencies={'on_complete': ['zone', 'linked_record_zone', 'submit']},
        disable_dependencies={'on_change': ['zone', 'linked_record_zone', 'select_one', 'submit']},
        should_cascade_disable_on_change=True,
        clear_dependencies={'on_change': ['zone', 'linked_record_zone', 'select_one']},
        should_cascade_clear_on_change=True
    )

    zone = Zone(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Alias Zone',
        required=True,
        enable_dependencies={'on_complete': ['name']},
        disable_dependencies={'on_change': ['name']},
        should_cascade_disable_on_change=True,
        clear_dependencies={'on_change': ['name']},
        should_cascade_clear_on_change=True
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
        enable_dependencies={'on_complete': ['host_record']},
        disable_dependencies={'on_change': ['host_record']},
        should_cascade_disable_on_change=True,
        clear_dependencies={'on_change': ['host_record']},
        should_cascade_clear_on_change=True
    )

    host_record = CustomStringField(
        label='Linked Record',
        required=True
    )

    submit = SubmitField(label='Submit')
