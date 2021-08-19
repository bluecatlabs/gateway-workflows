# Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates
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
# Date: 2021-08-23
# Gateway Version: 20.12.1
# Description: Example Gateway workflow

"""
Add static IPv4 address page
"""
import os

from flask import url_for, redirect, render_template, flash, g, request

from bluecat import route, util
import config.default_config as config
from main_app import app
from .add_static_ip4_address_form import GenericFormTemplate


def module_path():
    """
    Get module path.

    :return:
    """
    return os.path.dirname(os.path.abspath(str(__file__)))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, "/add_static_ip4_address/add_static_ip4_address_endpoint")
@util.workflow_permission_required("add_static_ip4_address_page")
@util.exception_catcher
def add_static_ip4_address_add_static_ip4_address_page():
    """
    Renders the form the user would first see when selecting the workflow.

    :return:
    """
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    return render_template(
        "add_static_ip4_address_page.html",
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )


@route(app, "/add_static_ip4_address/form", methods=["POST"])
@util.workflow_permission_required("add_static_ip4_address_page")
@util.exception_catcher
def add_static_ip4_address_add_static_ip4_address_page_form():
    """
    Processes the final form after the user has input all the required data.

    :return:
    """
    # pylint: disable=broad-except
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    if form.validate_on_submit():
        try:
            # Retrieve form attributes
            configuration = g.user.get_api().get_entity_by_id(form.configuration.data)
            selected_view = request.form.get("view", "")
            selected_hostname = request.form.get("hostname", "")
            hostinfo = ""
            if selected_view != "" and selected_hostname != "":
                view = configuration.get_view(selected_view)
                hostinfo = (
                    selected_hostname
                    + "."
                    + str(request.form.get("zone", ""))
                    + ","
                    + str(view.get_id())
                    + ","
                    + "true"
                    + ","
                    + "false"
                )
            properties = "name=" + form.description.data

            # Assign ip4 object
            ip4_object = configuration.assign_ip4_address(
                request.form.get("ip4_address", ""),
                form.mac_address.data,
                hostinfo,
                "MAKE_STATIC",
                properties,
            )

            # Put form processing code here
            g.user.logger.info(
                "Success - Static IP4 Address "
                + ip4_object.get_property("address")
                + " Added with Object ID: "
                + str(ip4_object.get_id())
            )
            flash(
                "Success - Static IP4 Address "
                + ip4_object.get_property("address")
                + " Added with Object ID: "
                + str(ip4_object.get_id()),
                "succeed",
            )
            page = "add_static_ip4_addressadd_static_ip4_address_add_static_ip4_address_page"
            return redirect(url_for(page))
        except Exception as e:
            flash(str(e))
            # Log error and render workflow page
            g.user.logger.warning(f"EXCEPTION THROWN: {e}")
            return render_template(
                "add_static_ip4_address_page.html",
                form=form,
                text=util.get_text(module_path(), config.language),
                options=g.user.get_options(),
            )
    else:
        g.user.logger.info("Form data was not valid.")
        return render_template(
            "add_static_ip4_address_page.html",
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
