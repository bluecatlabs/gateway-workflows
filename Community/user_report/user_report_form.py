#Copyright 2017 BlueCat Networks (USA) Inc. and its affiliates
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#http://www.apache.org/licenses/LICENSE-2.0
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
#By: Bill Morton (bmorton@bluecatnetworks.com)
#Date: 06-12-2017
#Gateway Version: 17.10.1

# Copyright 2017 BlueCat Networks. All rights reserved.

import datetime

from wtforms import StringField, PasswordField, SelectField, FileField, RadioField, BooleanField, DateTimeField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Email, MacAddress, IPAddress, URL
from bluecat.wtform_extensions import GatewayForm, validate_element_in_tuple
from bluecat.wtform_fields import *


class GenericFormTemplate(GatewayForm):
    # When updating the form, remember to make the corresponding changes to the workflow pages
    workflow_name = 'user_report'
    workflow_permission = 'user_report_page'

    reporttype = CustomSelectField(
        label='Report Type',
        choices=[('ALL_USERS', 'All Users'),('GUI', 'All GUI Users'), ('API', 'All API Users'), ('GUI_AND_API', 'All GUI and API Users'), ('BY_GROUPS', 'By Groups')],
        clear_below_on_change=False,
        is_disabled_on_start=False,
        # Javascript call below to enable/disable usergroups
        on_complete=['by_groups'],
        enable_on_complete=['submit']
    )

    #List of all Address Manager Groups by API
    usergroups = CustomSelectField(
        'Address Manager Groups',
        coerce=int,
        enable_on_complete=['submit'],
        required=False
    )

    submit = SubmitField(label='Submit')
