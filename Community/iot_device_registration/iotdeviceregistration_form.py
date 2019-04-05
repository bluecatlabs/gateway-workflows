#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
# By: Muhammad Heidir (mheidir@bluecatnetworks.com)
# Date: 03-04-2019
# Gateway Version: 18.10.2
# Description: Bulk IoT Device Registration/De-Registration workflow for BlueCat Gateway

"""
Workflow form template
"""
import datetime

from wtforms import StringField, PasswordField, FileField
from wtforms import BooleanField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Email, MacAddress, URL
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import Configuration, CustomStringField, IP4Address


class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'iotdeviceregistration'
    workflow_permission = 'iotdeviceregistration_page'

    name = CustomStringField(
        label='NAME',
        is_disabled_on_start=False,
        required=True,
        validators=[DataRequired()]
    )
    
    email = CustomStringField(
        label='Email',
        is_disabled_on_start=False,
        required=True,
        default='e@e.com',
        validators=[DataRequired(), Email()]
    )
    
    file = FileField(
        label='File'
    )

    submit = SubmitField(
        label='Submit'
    )
