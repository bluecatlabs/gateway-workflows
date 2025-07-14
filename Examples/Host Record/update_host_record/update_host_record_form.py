# Copyright 2020-2025 BlueCat Networks (USA) Inc. and its affiliates
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
# Date: 2025-07-31
# Gateway Version: 25.2.0
# Description: Example Gateway workflow

"""
Update host record form
"""
from wtforms import SubmitField
from bluecat.wtform_fields import (
    Configuration,
    View,
    Zone,
    HostRecord,
    CustomStringField,
    PlainHTML,
    CustomBooleanField,
)
from bluecat.server_endpoints import get_host_records_endpoint
from bluecat.wtform_extensions import GatewayForm


class GenericFormTemplate(GatewayForm):
    """Form to generate HTML and Javascript for the update_host_record workflow

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """

    workflow_name = "update_host_record"
    workflow_permission = "update_host_record_page"
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
        inputs={"zone": "parent_zone", "configuration": "configuration", "view": "view"},
        clear_below_on_change=False,
        enable_dependencies={"on_complete": ["host_record"]},
        disable_dependencies={"on_change": ["host_record"]},
        clear_dependencies={"on_change": ["host_record", "name", "ip4_address"]},
        should_cascade_disable_on_change=True,
        should_cascade_clear_on_change=True,
    )

    host_record = HostRecord(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label="Host Record",
        required=True,
        inputs={
            "configuration": "configuration",
            "view": "view",
            "parent_zone": "parent_zone",
            "host_record": "host_record",
        },
        server_outputs={"on_complete": {"name": "name", "addresses": "ip4_address"}},
        server_side_output_method=get_host_records_endpoint,
        clear_below_on_change=False,
        enable_dependencies={"on_complete": ["submit", "name", "ip4_address", "deploy_now"]},
        disable_dependencies={"on_change": ["submit", "name", "ip4_address", "deploy_now"]},
        should_cascade_disable_on_change=True,
    )

    separator = PlainHTML("<hr>")

    name = CustomStringField(label="New Host Name", required=True)

    ip4_address = CustomStringField(
        label="IPv4 Address (multiple IPv4 addresses must be separated by a comma)", required=True
    )

    deploy_now = CustomBooleanField(label="Deploy Now")

    submit = SubmitField(label="Update")
