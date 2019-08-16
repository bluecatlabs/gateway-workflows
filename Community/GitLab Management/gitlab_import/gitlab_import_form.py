# Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
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
# Date: 2019-07-01
# Gateway Version: 19.5.1
# Description: Community Gateway workflow


"""
Workflow form template
"""

from wtforms import SubmitField
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import CustomStringField
from . import gitlab_import_config
from .custom_wtform_fields import gitlab_import_entities


class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'gitlab_import'
    workflow_permission = 'gitlab_import_page'
    default_group = CustomStringField(
        label='Default GitLab Group',
        default=gitlab_import_config.default_group,
        is_disabled_on_start=True,
        is_disabled_on_error=True,
        required=True
    )

    gitlab_groups = gitlab_import_entities.GitlabGroups(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='GitLab Projects/Sub Groups',
        required=True,
        coerce=int,
        validators=[],
        is_disabled_on_start=False,
        on_complete=[],
        clear_below_on_change=False,
        enable_dependencies={'on_complete': ['submit']}
    )

    submit = SubmitField(label='Import')

