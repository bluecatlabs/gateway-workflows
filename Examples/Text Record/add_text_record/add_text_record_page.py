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
Add text record page
"""
import os

from flask import url_for, redirect, render_template, flash, g, request

from bluecat import route, util
import config.default_config as config
from main_app import app
from .add_text_record_form import GenericFormTemplate


def module_path():
    """
    Get module path.

    :return:
    """
    return os.path.dirname(os.path.abspath(str(__file__)))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, "/add_text_record/add_text_record_endpoint")
@util.workflow_permission_required("add_text_record_page")
@util.exception_catcher
def add_text_record_add_text_record_page():
    """
    Renders the form the user would first see when selecting the workflow.

    :return:
    """
    form = GenericFormTemplate()
    return render_template(
        "add_text_record_page.html",
        form=form,
        text=util.get_text(module_path(), config.language),
    )


@route(app, "/add_text_record/form", methods=["POST"])
@util.workflow_permission_required("add_text_record_page")
@util.exception_catcher
def add_text_record_add_text_record_page_form():
    """
    Processes the final form after the user has input all the required data.

    :return:
    """
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    if form.validate_on_submit():
        try:
            # Retrieve configuration, view, and absolute name
            configuration = g.user.get_api().get_entity_by_id(form.configuration.data)
            view = configuration.get_view(request.form["view"])
            absolute_name = form.name.data + "." + request.form.get("zone", "")

            # Attempt to add the text record
            text_record = view.add_text_record(absolute_name, form.text.data)

            g.user.logger.info(
                "Success-Text Record "
                + text_record.get_property("absoluteName")
                + " Added with Object ID: "
                + str(text_record.get_id())
            )
            flash(
                "Success - Text Record "
                + text_record.get_property("absoluteName")
                + " Added with Object ID: "
                + str(text_record.get_id()),
                "succeed",
            )
            return redirect(url_for("add_text_recordadd_text_record_add_text_record_page"))

        except Exception as e:
            flash(str(e))
            # Log error and render workflow page
            g.user.logger.warning(f"EXCEPTION THROWN: {e}")
            return render_template(
                "add_text_record_page.html",
                form=form,
                text=util.get_text(module_path(), config.language),
            )
    else:
        g.user.logger.info("Form data was not valid.")
        return render_template(
            "add_text_record_page.html",
            form=form,
            text=util.get_text(module_path(), config.language),
        )
