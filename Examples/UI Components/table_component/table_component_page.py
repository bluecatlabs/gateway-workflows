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
Table component page
"""
import os

from flask import render_template

from bluecat import route
from bluecat import util

import config.default_config as config
from .table_component_form import GenericFormTemplate
from main_app import app


def module_path():
    """
    Get module path.

    :return:
    """
    return os.path.dirname(os.path.abspath(str(__file__)))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, "/table_component/table_component_endpoint")
@util.workflow_permission_required("table_component_page")
@util.exception_catcher
def table_component_table_component_page():
    """
    Renders the form the user would first see when selecting the workflow.

    :return:
    """
    form = GenericFormTemplate()
    return render_template(
        "table_component_page.html",
        form=form,
        text=util.get_text(module_path(), config.language),
    )
