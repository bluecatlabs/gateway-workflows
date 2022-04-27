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
# Date: 2022-04-28
# Gateway Version: 22.4.1
# Description: Example Gateway workflow

"""
Update IPv4 address page
"""
import os

from flask import url_for, redirect, render_template, flash, g, request

from bluecat import route, util
from bluecat.api_exception import APIException
import config.default_config as config
from main_app import app
from .update_ip4_address_form import GenericFormTemplate


def module_path():
    """
    Get module path.

    :return:
    """
    return os.path.dirname(os.path.abspath(str(__file__)))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, "/update_ip4_address/update_ip4_address_endpoint")
@util.workflow_permission_required("update_ip4_address_page")
@util.exception_catcher
def update_ip4_address_update_ip4_address_page():
    """
    Renders the form the user would first see when selecting the workflow.

    :return:
    """
    form = GenericFormTemplate()
    return render_template(
        "update_ip4_address_page.html",
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )


@route(app, "/update_ip4_address/form", methods=["POST"])
@util.workflow_permission_required("update_ip4_address_page")
@util.exception_catcher
def update_ip4_address_update_ip4_address_page_form():
    """
    Processes the final form after the user has input all the required data.

    :return:
    """
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    if form.validate_on_submit():
        try:
            # Retrieve form attributes
            configuration = g.user.get_api().get_entity_by_id(form.configuration.data)

            # Retrieve the IP4 address object
            ip4_address = configuration.get_ip4_address(request.form.get("ip4_address", ""))

            # Update the form name and mac address properties
            ip4_address.set_name(form.description.data)
            ip4_address.set_property("macAddress", form.mac_address.data)
            ip4_address.update()

            # Put form processing code here
            g.user.logger.info(
                "Success - IP4 Address Modified - Object ID: " + str(ip4_address.get_id())
            )
            flash(
                "Success - IP4 Address Modified - Object ID: " + str(ip4_address.get_id()),
                "succeed",
            )
            return redirect(url_for("update_ip4_addressupdate_ip4_address_update_ip4_address_page"))
        except APIException as e:
            flash(str(e))
            # Log error and render workflow page
            g.user.logger.warning(f"EXCEPTION THROWN: {e}")
            return render_template(
                "update_ip4_address_page.html",
                form=form,
                text=util.get_text(module_path(), config.language),
                options=g.user.get_options(),
            )
    else:
        g.user.logger.info("Form data was not valid.")
        return render_template(
            "update_ip4_address_page.html",
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
