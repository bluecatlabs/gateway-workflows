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
# Description: Register MAC Address Form

import datetime
import os

from flask_wtf.form import FlaskForm
from wtforms import StringField, SelectField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, MacAddress

from bluecat import util
import config.default_config as config

from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import CustomStringField, CustomSelectField, CustomSubmitField

def module_path():
    return os.path.dirname(os.path.abspath(str(__file__)))

def get_resource_text():
    return util.get_text(module_path(), config.language)

class GenericFormTemplate(GatewayForm):
    # When updating the form, remember to make the corresponding changes to the workflow pages
    workflow_name = 'register_mac_address'
    workflow_permission = 'register_mac_address_page'
    
    text = get_resource_text()
    require_message=text['require_message']
    
    mac_address = CustomStringField(
        label=text['label_mac_address'],
        default='FF:FF:FF:FF:FF:FF',
        is_disabled_on_start=False,
        validators=[DataRequired(message=require_message), MacAddress()]
    )
    
    device_group = CustomSelectField(
        label=text['label_device_group'],
        coerce=int,
        is_disabled_on_start=False,
        validators=[]
    )

    asset_code = CustomStringField(
        label=text['label_asset_code'],
        is_disabled_on_start=False,
        validators=[DataRequired(message=require_message)]
    )
    
    employee_code = CustomStringField(
        label=text['label_employee_code'],
        is_disabled_on_start=False,
        validators=[DataRequired(message=require_message)]
    )

    location = CustomSelectField(
        label=text['label_location'],
        coerce=int,
        is_disabled_on_start=False
    )
    
    submit_date = DateTimeField(
        label=text['label_submit_date'],
        default=datetime.datetime.now(),
        format='%Y/%m/%d'
    )
    
    expiry_date = DateTimeField(
        label=text['label_expiry_date'],
        default=datetime.datetime.now() + datetime.timedelta(days=365),
        format='%Y/%m/%d'
    )

    submit = CustomSubmitField(
        label=text['label_submit'],
        is_disabled_on_start=False
    )
