# Copyright 2017 BlueCat Networks. All rights reserved.

import datetime

from wtforms import SubmitField
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import *
from .wtform_fields_custom import Group


class GenericFormTemplate(GatewayForm):
    # When updating the form, remember to make the corresponding changes to the workflow pages
    workflow_name = 'update_user_permissions'
    workflow_permission = 'update_user_permissions_page'
    groups = Group(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Address Manager User Groups',
        required=True,
        coerce=int,
        validators=[],
        is_disabled_on_start=False,
        on_complete=[],
        enable_on_complete=['gateway_groups', 'submit'],
        clear_below_on_change=False
    )
    gateway_groups = CustomSelectField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Gateway Group',
        required=True,
        choices=[('admin', 'admin'), ('all', 'all')],
        enable_on_complete=['submit'],
        result_decorator=None
    )

    submit = SubmitField(label='Submit')
