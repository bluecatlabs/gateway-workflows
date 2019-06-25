# Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
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
# Description: Flip Main-DR Servers Form

import os

from flask import g

from bluecat import tag, util
import config.default_config as config

from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import CustomSelectField
from bluecat.wtform_fields import CustomSubmitField
from bluecat.wtform_fields import TableField

def module_path():
    return os.path.dirname(os.path.abspath(str(__file__)))

def get_resource_text():
    return util.get_text(module_path(), config.language)

def raw_table_data(*args, **kwargs):
    """Returns table formatted data for display in the TableField component"""
    # pylint: disable=unused-argument
    text = get_resource_text()
    return {
        "columns": [
            {"title": text['title_full_name']},
            {"title": text['title_state']},
            {"title": text['title_ip_address']},
        ],
        "data": []
    }

def get_applications(default_val=False):
    """Return all implemented Entity types formatted for a CustomSelectField"""
    text = get_resource_text()
    result = []
    if g.user:
        if default_val:
            result.append((0, text['instruction']))

        tag_group = g.user.get_api().get_tag_group_by_name('BCPGroup')
        children = tag_group.get_tags()
        for c in children:
            result.append((c.get_id(), c.get_name()))

    result.sort()

    return result

class GenericFormTemplate(GatewayForm):
    # When updating the form, remember to make the corresponding changes to the workflow pages
    workflow_name = 'flip_normal_dr'
    workflow_permission = 'flip_normal_dr_page'

    text = get_resource_text()

    application = CustomSelectField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label=text['label_application'],
        choices_function=get_applications,
        coerce=int,
        is_disabled_on_start=False,
        validators=[]
    )

    server_list = TableField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label=text['label_list'],
        data_function=raw_table_data,
        table_features={
            'searching': False,
            'ordering': False,
            'info': False,
            'lengthChange': False
        },
        is_disabled_on_start=True,
        is_disabled_on_error=True
    )

    submit = CustomSubmitField(
        label=text['label_submit'],
        is_disabled_on_start=True,
        is_disabled_on_error=True
    )
