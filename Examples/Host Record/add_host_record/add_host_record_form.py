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
# Date: 2021-12-15
# Gateway Version: 21.5.1
# Description: Example Gateway workflow

"""
Add host record form
"""
from wtforms import SubmitField
from bluecat.wtform_fields import (
    Configuration,
    View,
    Zone,
    IP4Address,
    CustomStringField,
    CustomBooleanField,
)
from bluecat.wtform_extensions import GatewayForm


def filter_reserved(res):
    """
    Filter reserved IP.

    :param res:
    :return:
    """
    try:
        if res["data"]["state"] == "RESERVED":
            res["status"] = "FAIL"
            res["message"] = "Host records cannot be added if ip address is reserved."
        return res
    except (TypeError, KeyError):
        return res


class GenericFormTemplate(GatewayForm):
    """Form to generate HTML and Javascript for the add_host_record workflow

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """

    workflow_name = "add_host_record"
    workflow_permission = "add_host_record_page"
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
        on_complete=["call_zone"],
        clear_below_on_change=False,
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
        clear_below_on_change=False,
        enable_dependencies={"on_complete": ["ip4_address"]},
        disable_dependencies={"on_change": ["ip4_address"]},
        clear_dependencies={"on_change": ["ip4_address", "hostname"]},
        should_cascade_disable_on_change=True,
        should_cascade_clear_on_change=True,
    )

    ip4_address = IP4Address(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label="IP Address",
        required=True,
        inputs={"configuration": "configuration", "address": "ip4_address"},
        result_decorator=filter_reserved,
        clear_below_on_change=False,
        enable_dependencies={"on_complete": ["hostname", "submit", "deploy_now"]},
        disable_dependencies={"on_change": ["hostname", "submit", "deploy_now"]},
        should_cascade_disable_on_change=True,
    )

    hostname = CustomStringField(label="Hostname", required=True)

    deploy_now = CustomBooleanField(label="Deploy Now")

    submit = SubmitField(label="Submit")
