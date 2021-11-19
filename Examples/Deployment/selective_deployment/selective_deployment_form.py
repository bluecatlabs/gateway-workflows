# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates
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
# Date: 2021-11-22
# Gateway Version: 21.5.1
# Description: Example Gateway workflow

"""this file is used to add different elements into the page"""
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import Configuration, View, Zone
from bluecat.wtform_fields import CustomSearchButtonField, CustomButtonField
from bluecat.wtform_fields import TableField

from .component_logic import find_objects_by_type_endpoint
from .component_logic import raw_table_data


class GenericFormTemplate(GatewayForm):
    """class used to structure all the elements on the page"""

    workflow_name = "selective_deployment"
    workflow_permission = "selective_deployment_page"

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
        enable_dependencies={"on_complete": ["zone"]},
        disable_dependencies={"on_change": ["zone"]},
        clear_dependencies={"on_change": ["zone"]},
        should_cascade_disable_on_change=True,
        should_cascade_clear_on_change=True,
    )

    zone = Zone(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label="Zone",
        required=True,
        start_initialized=True,
        display_message=True,
        inputs={"zone": "zone", "configuration": "configuration", "view": "view"},
        clear_below_on_change=False,
        enable_dependencies={"on_complete": ["search"]},
        disable_dependencies={"on_change": ["search"], "on_click": ["search"]},
        clear_dependencies={"on_change": ["search"], "on_click": ["search"]},
        should_cascade_disable_on_change=True,
        should_cascade_clear_on_change=True,
    )

    search = CustomSearchButtonField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        default="Search Objects",
        inputs={"zone": "zone", "view": "view", "configuration": "configuration"},
        server_side_method=find_objects_by_type_endpoint,
        display_message=True,
        label="SEARCH DNS",
        on_complete=["call_output_table"],
        enable_dependencies={"on_complete": ["deploy", "output_table"]},
        disable_dependencies={"on_change": ["deploy", "output_table"]},
        clear_below_on_change=False,
        should_cascade_disable_on_change=True,
        should_cascade_clear_on_change=True,
    )

    output_table = TableField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label="",
        data_function=raw_table_data,
        table_features={"lengthMenu": [10, 20, 30, 40, 50, 100, 500, 1000]},
    )

    deploy = CustomButtonField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label="Deploy",
        display_message=True,
    )
