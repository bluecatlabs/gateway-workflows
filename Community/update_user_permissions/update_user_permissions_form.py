# Copyright 2017 BlueCat Networks (USA) Inc. and its affiliates
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# By: Bill Morton (bmorton@bluecatnetworks.com)
# Date: 06-12-2017
# Gateway Version: 17.10.1

# Copyright 2017 BlueCat Networks. All rights reserved.

import datetime

from wtforms import SubmitField
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import *
from .wtform_fields_custom import Group


class GenericFormTemplate(GatewayForm):
    # When updating the form, remember to make the corresponding changes to the workflow pages
    workflow_name = 'update_user_permissions'
    workflow_permission = 'update_user_permissions_page'
    groups = Group(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Address Manager User Groups',
        required=True,
        coerce=int,
        validators=[],
        is_disabled_on_start=False,
        on_complete=[],
        enable_on_complete=['gateway_groups', 'submit'],
        clear_below_on_change=False
    )
    gateway_groups = CustomSelectField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Gateway Group',
        required=True,
        choices=[('admin', 'admin'), ('all', 'all')],
        enable_on_complete=['submit'],
        result_decorator=None
    )

    submit = SubmitField(label='Submit')
