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
# Description: Bulk Register MAC Address Form

import os

from wtforms import FileField, SubmitField

from bluecat import util
import config.default_config as config

from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import CustomSubmitField
from bluecat.wtform_fields import TableField

def module_path():
    return os.path.dirname(os.path.abspath(str(__file__)))

def get_resource_text():
    return util.get_text(module_path(), config.language)
    
def table_features():
    """Returns table formatted data for display in the TableField component"""
    # pylint: disable=unused-argument
    text = get_resource_text()
    
    return {
        "columns": [
            {"title": text['label_asset_code'], 'width': 80},
            {"title": text['label_mac_address'], 'width': 80},
            {"title": text['label_mac_pool'], 'width': 100},
            {"title": text['label_comments'], 'width': 140}
        ],
        "columnDefs": [],
        "searching": False,
        "ordering": False,
        "info": False,
        "lengthChange": False,
        "data": []
    }


class GenericFormTemplate(GatewayForm):
    # When updating the form, remember to make the corresponding changes to the workflow pages
    workflow_name = 'bulk_register_mac_address'
    workflow_permission = 'bulk_register_mac_address_page'
    
    text = get_resource_text()

    file = FileField(text['label_file'])

    mac_address_list = TableField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label=text['label_list'],
        table_features=table_features(),
        is_disabled_on_start=False
    )
    
    submit = CustomSubmitField(
        label=text['label_submit'],
        is_disabled_on_start=True,
        is_disabled_on_error=True
    )

