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
Delete alias record page
"""
import os

from flask import url_for, redirect, render_template, flash, g, request

from bluecat import route, util
import config.default_config as config
from main_app import app
from .delete_alias_record_form import GenericFormTemplate


def module_path():
    """
    Get module path.

    :return:
    """
    return os.path.dirname(os.path.abspath(str(__file__)))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, "/delete_alias_record/delete_alias_record_endpoint")
@util.workflow_permission_required("delete_alias_record_page")
@util.exception_catcher
def delete_alias_record_delete_alias_record_page():
    """
    Renders the form the user would first see when selecting the workflow.

    :return:
    """
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    return render_template(
        "delete_alias_record_page.html",
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )


@route(app, "/delete_alias_record/form", methods=["POST"])
@util.workflow_permission_required("delete_alias_record_page")
@util.exception_catcher
def delete_alias_record_delete_alias_record_page_form():
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
            # Retrieve form attributes and declare variables
            configuration = g.user.get_api().get_entity_by_id(form.configuration.data)
            view = configuration.get_view(request.form["view"])

            # Retrieve alias record
            alias_record = view.get_alias_record(
                request.form["alias_record"] + "." + request.form["zone"]
            )

            # Retrieve alias_record attributes for flash message
            alias_name = alias_record.get_name()
            alias_id = str(alias_record.get_id())

            # Delete alias record
            alias_record.delete()

            # Put form processing code here
            g.user.logger.info(
                "Success - Alias Record " + alias_name + " Deleted with Object ID: " + alias_id
            )
            flash(
                "Success - Alias Record " + alias_name + " Deleted with Object ID: " + alias_id,
                "succeed",
            )
            return redirect(
                url_for("delete_alias_recorddelete_alias_record_delete_alias_record_page")
            )
        except Exception as e:
            flash(str(e))
            g.user.logger.warning(f"EXCEPTION THROWN: {e}")
            return render_template(
                "delete_alias_record_page.html",
                form=form,
                text=util.get_text(module_path(), config.language),
                options=g.user.get_options(),
            )
    else:
        g.user.logger.info("Form data was not valid.")
        return render_template(
            "delete_alias_record_page.html",
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
