# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates
# -*- coding: utf-8 -*-
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
# Date: 2019-03-14
# Gateway Version: 18.10.2
# Description: Lease History IP Form

import os

from wtforms.validators import DataRequired, IPAddress

from bluecat import util
import config.default_config as config

from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import CustomStringField
from bluecat.wtform_fields import CustomSearchButtonField
from bluecat.wtform_fields import TableField

from .lease_history_ip_access import get_resource_text
from .lease_history_ip_access import raw_table_data
from .lease_history_ip_access import query_history_by_ip_endpoint

class GenericFormTemplate(GatewayForm):
    workflow_name = 'lease_history_ip'
    workflow_permission = 'lease_history_ip_page'

    text = get_resource_text()

    ip_address = CustomStringField(
        label=text['label_ip_address'],
        default='10.0.0.0',
        validators=[DataRequired(message=text['require_message']), IPAddress()],
        required=True,
        is_disabled_on_start=False
    )

    query_history = CustomSearchButtonField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label=text['label_query'],
        default='Search Objects',
        inputs={'ip_address': 'ip_address'},
        server_side_method=query_history_by_ip_endpoint,
        display_message=True,
        on_complete=['call_output_table'],
        is_disabled_on_start=False
    )

    output_table = TableField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='',
        data_function=raw_table_data,
        table_features={
            'searching': False,
            'ordering': False,
            'info': False,
            'lengthChange': False
        },
        is_disabled_on_start=False
    )

