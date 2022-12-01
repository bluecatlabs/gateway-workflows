# Copyright 2020-2022 BlueCat Networks (USA) Inc. and its affiliates
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
# Date: 2022-11-30
# Gateway Version: 22.11.1
# Description: Example Gateway workflow

"""
Update text record form
"""
from bluecat.wtform_fields import (
    Configuration,
    View,
    Zone,
    CustomStringField,
    CustomSearchButtonField,
)
from bluecat.wtform_fields import FilteredSelectField, PlainHTML, CustomSubmitField
from bluecat.wtform_extensions import GatewayForm
from bluecat.server_endpoints import get_text_records_endpoint


class GenericFormTemplate(GatewayForm):
    """Form to generate HTML and Javascript for the update_text_record workflow

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """

    workflow_name = "update_text_record"
    workflow_permission = "update_text_record_page"
    configuration = Configuration(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label="Configuration",
        required=True,
        coerce=int,
        clear_below_on_change=False,
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
        clear_below_on_change=False,
        display_message=True,
        enable_dependencies={"on_complete": ["parent_zone"]},
        disable_dependencies={"on_change": ["parent_zone"]},
        clear_dependencies={"on_change": ["parent_zone"]},
        should_cascade_disable_on_change=True,
        should_cascade_clear_on_change=True,
    )

    parent_zone = Zone(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label="Zone",
        required=True,
        start_initialized=True,
        display_message=True,
        inputs={"zone": "parent_zone", "configuration": "configuration", "view": "view"},
        clear_below_on_change=False,
        enable_dependencies={"on_complete": ["text_record", "search"]},
        disable_dependencies={"on_change": ["text_record", "search"]},
        clear_dependencies={"on_change": ["text_record", "search"]},
        should_cascade_disable_on_change=True,
        should_cascade_clear_on_change=True,
    )

    text_record = CustomStringField(label="Text Record")

    search = CustomSearchButtonField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        default="Search",
        inputs={
            "configuration": "configuration",
            "view": "view",
            "parent_zone": "parent_zone",
            "name": "text_record",
        },
        server_side_method=get_text_records_endpoint,
        display_message=True,
        on_complete=["call_txt_list"],
        enable_dependencies={"on_complete": ["txt_filter", "txt_list"]},
        disable_dependencies={
            "on_change": ["txt_filter", "txt_list"],
            "on_click": ["txt_filter", "txt_list"],
        },
        clear_dependencies={
            "on_change": ["txt_filter", "txt_list"],
            "on_click": ["txt_filter", "txt_list"],
        },
        should_cascade_disable_on_change=True,
        should_cascade_clear_on_change=True,
    )

    txt_filter = CustomStringField(label="Filter", is_disabled_on_error=True)

    txt_list = FilteredSelectField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label="Text",
        size=12,
        filter_field="txt_filter",
        choices=[(0, "")],
        coerce=int,
        is_disabled_on_error=True,
        on_complete=["call_name_js", "call_text"],
        inputs={
            "configuration": "configuration",
            "view": "view",
            "parent_zone": "parent_zone",
            "name": "text_record",
        },
        clear_dependencies={"on_change": ["name", "text"]},
        server_side_method=get_text_records_endpoint,
        enable_dependencies={"on_complete": ["name", "text", "submit"]},
        disable_dependencies={"on_change": ["name", "text", "submit"]},
        should_cascade_disable_on_change=True,
        should_cascade_clear_on_change=True,
    )

    plain_1 = PlainHTML("<hr>")

    name = CustomStringField(label="New Name", is_disabled_on_error=True)

    text = CustomStringField(
        label="New Text", inputs={"text": "txt_list"}, is_disabled_on_error=True
    )

    submit = CustomSubmitField(label="Update")
