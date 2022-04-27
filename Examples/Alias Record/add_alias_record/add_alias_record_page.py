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
Add alias record page
"""
import os

from flask import url_for, redirect, render_template, flash, g, request

from bluecat import route, util
import config.default_config as config
from main_app import app
from .add_alias_record_form import GenericFormTemplate


def module_path():
    """
    Get module path.

    :return:
    """
    return os.path.dirname(os.path.abspath(str(__file__)))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, "/add_alias_record/add_alias_record_endpoint")
@util.workflow_permission_required("add_alias_record_page")
@util.exception_catcher
def add_alias_record_add_alias_record_page():
    """
    Renders the form the user would first see when selecting the workflow.

    :return:
    """
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    return render_template(
        "add_alias_record_page.html",
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )


@route(app, "/add_alias_record/form", methods=["POST"])
@util.workflow_permission_required("add_alias_record_page")
@util.exception_catcher
def add_alias_record_add_alias_record_page_form():
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
            view = configuration.get_view(request.form["view"])
            alias_name = request.form["name"] + "." + request.form["zone"]

            # Create the alias record object
            alias_record = view.add_alias_record(
                alias_name, request.form["host_record"] + "." + request.form["linked_record_zone"]
            )

            # Put form processing code here
            g.user.logger.info(
                "Success - Alias Record "
                + alias_record.get_name()
                + " Added with Object ID: "
                + str(alias_record.get_id())
            )
            flash(
                "Success - Alias Record "
                + alias_record.get_name()
                + " Added with Object ID: "
                + str(alias_record.get_id()),
                "succeed",
            )
            return redirect(url_for("add_alias_recordadd_alias_record_add_alias_record_page"))

        except Exception as e:
            flash(str(e))
            # Log error and render workflow page
            g.user.logger.warning(f"EXCEPTION THROWN: {e}")
            return render_template(
                "add_alias_record_page.html",
                form=form,
                text=util.get_text(module_path(), config.language),
                options=g.user.get_options(),
            )
    else:
        g.user.logger.info("Form data was not valid.")
        return render_template(
            "add_alias_record_page.html",
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
