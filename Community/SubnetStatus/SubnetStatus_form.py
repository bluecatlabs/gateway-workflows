# Copyright 2017 BlueCat Networks. All rights reserved.

import datetime

from wtforms import StringField, PasswordField, SelectField, FileField, RadioField, BooleanField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Email, MacAddress, IPAddress, URL
from bluecat.wtform_extensions import GatewayForm, validate_element_in_tuple
from bluecat.wtform_fields import *


class GenericFormTemplate(GatewayForm):
    workflow_name = 'SubnetStatus'
    workflow_permission = 'SubnetStatus_page'

    subnetsearch = CustomStringField(
        label='Enter Subnet to search'
    )
    search_button = PlainHTML('<div id = "find_subnets_button"><input id="find_subnets" type="button" value="Search">'
                              '</div><br><br><br><br><br><br>')

    loading = PlainHTML(
        '<div id="loading">Loading subnets and report</div>')

    subnet = NoPreValidationSelectField(
        label='Choose subnet from list below',
        coerce=int,
        choices=[]
    )

    email = CustomStringField(
        label='Email',
        is_disabled_on_start=False,
        required=True
    )
    email_button = SubmitField(label='Email this Report')

    stats_display = PlainHTML('<br><div id="report"></div>')

