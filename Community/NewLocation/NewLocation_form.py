# Copyright 2019 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""
import datetime

from wtforms import StringField, PasswordField, FileField
from wtforms import BooleanField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Email, MacAddress, URL
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import Configuration, CustomStringField, IP4Address

from .NewLocation_utils import Location


class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'NewLocation'
    workflow_permission = 'NewLocation_page'
    parent_location = Location(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Parent Location',
        is_disabled_on_start=False,
        required=True
    )

    new_location_name = CustomStringField(
        label='New Location Name',
        is_disabled_on_start=False,
        required=True
    )

    new_location_code = CustomStringField(
        label='New Location Code',
        is_disabled_on_start=False,
        required=True
    )

    submit = SubmitField(label='Submit')
