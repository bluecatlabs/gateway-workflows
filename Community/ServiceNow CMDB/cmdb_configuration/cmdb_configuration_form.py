# Copyright 2020 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""
import datetime

from wtforms import StringField, PasswordField, FileField
from wtforms import BooleanField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Email, MacAddress, URL
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import Configuration, CustomStringField, IP4Address, CustomSubmitField
from . import cmdb_config


class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'cmdb_configuration'
    workflow_permission = 'cmdb_configuration_page'
    servicenow_url = CustomStringField(
        label='ServiceNow URL',
        default=cmdb_config.servicenow_url,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True,
    )

    servicenow_username = CustomStringField(
        label='ServiceNow User',
        default=cmdb_config.servicenow_username,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True
    )

    servicenow_secret_file = CustomStringField(
        label='ServiceNow Secret file and path',
        default=cmdb_config.servicenow_secret_file,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True
    )

    servicenow_max_query_results = CustomStringField(
        label='ServiceNow Max Query Results',
        default=cmdb_config.servicenow_username,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True
    )

    submit = CustomSubmitField(
        label='Save',
        is_disabled_on_start=False,
        is_disabled_on_error=False
    )