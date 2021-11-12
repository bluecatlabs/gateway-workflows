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
# Date: 2021-11-10
# Gateway Version: 18.10.2
# Description: Confirm MAC Address Form

import datetime
import os
import re


from flask_wtf.form import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Regexp, ValidationError

from bluecat import util
import config.default_config as config

from bluecat.wtform_extensions import GatewayForm

def module_path():
    return os.path.dirname(os.path.abspath(str(__file__)))

def get_resource_text():
    return util.get_text(module_path(), config.language)

class GenericFormTemplate(GatewayForm):
    # When updating the form, remember to make the corresponding changes to the workflow pages
    workflow_name = 'confirm_mac_address'
    workflow_permission = 'confirm_mac_address_page'
    
    text = get_resource_text()
    require_message = text['require_message']
    invalid_message = text['invalid_message']
    
    mac_address = StringField(
        label=text['label_mac_address'],
        default='FF:FF:FF:FF:FF:FF',
        validators=[
            DataRequired(message=require_message), 
            Regexp(r'^[0-9a-fA-F]{2}[:-]([0-9a-fA-F]{2}[:-]){4}[0-9a-fA-F]{2}$', message=invalid_message)
        ]
    )
    
    submit = SubmitField()
