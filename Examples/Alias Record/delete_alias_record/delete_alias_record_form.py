# Copyright 2020-2023 BlueCat Networks (USA) Inc. and its affiliates
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
# Date: 2023-08-30
# Gateway Version: 23.2.0
# Description: Example Gateway workflow

"""
Delete alias record form
"""
from wtforms import SubmitField
from bluecat.wtform_fields import Configuration, View, Zone, AliasRecord, CustomStringField
from bluecat.wtform_extensions import GatewayForm


class GenericFormTemplate(GatewayForm):
    """Form to generate HTML and Javascript for the delete_text_record workflow

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """

    workflow_name = "delete_alias_record"
    workflow_permission = "delete_alias_record_page"
    configuration = Configuration(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label="Configuration",
        required=True,
        coerce=int,
        is_disabled_on_start=False,
        on_complete=["call_view"],
        enable_dependencies={"on_complete": ["view"]},
        disable_dependencies={"on_change": ["view"]},
        clear_dependencies={"on_change": ["view"]},
    )

    view = View(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label="View",
        required=True,
        one_off=True,
        on_complete=["call_zone"],
        enable_dependencies={"on_complete": ["zone"]},
        disable_dependencies={"on_change": ["zone"]},
        should_cascade_disable_on_change=True,
        clear_dependencies={"on_change": ["zone"]},
        should_cascade_clear_on_change=True,
    )

    zone = Zone(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label="Zone",
        required=True,
        enable_dependencies={"on_complete": ["alias_record"]},
        disable_dependencies={"on_change": ["alias_record"]},
        should_cascade_disable_on_change=True,
        clear_dependencies={"on_change": ["alias_record"]},
        should_cascade_clear_on_change=True,
    )

    alias_record = AliasRecord(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label="Alias Record",
        required=True,
        on_complete=["populate_alias_record_data"],
        enable_dependencies={"on_complete": ["name", "linked_record", "submit"]},
        disable_dependencies={"on_change": ["name", "linked_record", "submit"]},
        should_cascade_disable_on_change=True,
        clear_dependencies={"on_change": ["name", "linked_record"]},
        should_cascade_clear_on_change=True,
    )

    name = CustomStringField(label="Name", readonly=True)

    linked_record = CustomStringField(label="Linked Record", readonly=True)

    submit = SubmitField(label="Delete")
