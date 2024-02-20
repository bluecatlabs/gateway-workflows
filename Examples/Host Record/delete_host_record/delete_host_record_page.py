# Copyright 2020-2024 BlueCat Networks (USA) Inc. and its affiliates
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
# Date: 2024-02-20
# Gateway Version: 24.1.0
# Description: Example Gateway workflow

"""
Delete host record page
"""
import os

from flask import url_for, redirect, render_template, flash, g, request, jsonify

from bluecat import route, util
from bluecat.constants import SelectiveDeploymentStatus
from bluecat.server_endpoints import get_result_template, empty_decorator
import config.default_config as config
from main_app import app
from .delete_host_record_form import GenericFormTemplate


def module_path():
    """
    Get module path.

    :return:
    """
    return os.path.dirname(os.path.abspath(str(__file__)))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, "/delete_host_record/delete_host_record_endpoint")
@util.workflow_permission_required("delete_host_record_page")
@util.exception_catcher
def delete_host_record_delete_host_record_page():
    """
    Renders the form the user would first see when selecting the workflow.

    :return:
    """
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    return render_template(
        "delete_host_record_page.html",
        form=form,
        text=util.get_text(module_path(), config.language),
    )


@route(app, "/delete_host_record/form", methods=["POST"])
@util.workflow_permission_required("delete_host_record_page")
@util.exception_catcher
def delete_host_record_delete_host_record_page_form():
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

            # Retrieve host record
            host_record = view.get_host_record(
                request.form["host_record"] + "." + request.form["parent_zone"]
            )

            # Retrieve host record attributes for flash message
            host_record_name = host_record.get_property("absoluteName")
            host_record_id = str(host_record.get_id())

            # Delete host record
            host_record.delete()

            # Put form processing code here
            success_msg = f"Success - Host (A) Record {host_record_name} deleted with object ID: {host_record_id}"
            g.user.logger.info(success_msg)
            flash(success_msg, "succeed")

            # Perform Selective Deployment (RELATED Scope) on host record if checkbox is checked
            if form.deploy_now.data:
                entity_id_list = [host_record.get_id()]
                deploy_token = g.user.get_api().selective_deploy(entity_id_list)
                return render_template(
                    "delete_host_record_page.html",
                    form=form,
                    status_token=deploy_token,
                    text=util.get_text(module_path(), config.language),
                )
            return redirect(url_for("delete_host_recorddelete_host_record_delete_host_record_page"))
        except Exception as e:
            flash(str(e))
            # Log error and render workflow page
            g.user.logger.warning(f"EXCEPTION THROWN: {e}")
            return render_template(
                "delete_host_record_page.html",
                form=form,
                text=util.get_text(module_path(), config.language),
            )
    else:
        g.user.logger.info("Form data was not valid.")
        return render_template(
            "delete_host_record_page.html",
            form=form,
            text=util.get_text(module_path(), config.language),
        )


@route(app, "/delete_host_record/get_deploy_status", methods=["POST"])
@util.rest_workflow_permission_required("delete_host_record_page")
@util.rest_exception_catcher
def get_deploy_status():
    """
    Retrieves and updates deployment task status
    :return:
    """
    result = get_result_template()
    deploy_token = request.form["deploy_token"]
    try:
        task_status = g.user.get_api().get_deployment_task_status(deploy_token)
        result["status"] = task_status["status"]

        if task_status["status"] == SelectiveDeploymentStatus.FINISHED:
            deploy_errors = task_status["response"]["errors"]

            # Deployment failed
            if deploy_errors:
                result["data"] = "FAILED"
                result["message"] = deploy_errors
                raise Exception("Deployment Error: " + str(deploy_errors))

            # Deployment succeeded
            if task_status["response"]["views"]:
                task_result = task_status["response"]["views"][0]["zones"][0]["records"][0][
                    "result"
                ]
                result["data"] = task_result

            # Deployment finished with no changes
            else:
                result["data"] = "FINISHED"

            g.user.logger.info("Deployment Task Status: " + str(task_status))

        # Deployment queued/started
        else:
            result["data"] = task_status["status"]
    except Exception as e:
        g.user.logger.warning(e)

    return jsonify(empty_decorator(result))
