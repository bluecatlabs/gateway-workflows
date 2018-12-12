# Copyright 2018 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""
from wtforms.validators import DataRequired
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import (
    Configuration, CustomBooleanField, CustomPasswordField, CustomStringField, CustomSubmitField
)


class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'cisco_aci_example'
    workflow_permission = 'cisco_aci_page'

    apic_ip = CustomStringField(
        label='APIC IP',
        required=True,
        default='',
        validators=[DataRequired()],
        is_disabled_on_start=False,
    )

    apic_username = CustomStringField(
        label='APIC USERNAME',
        default='',
        required=True,
        validators=[DataRequired()],
        is_disabled_on_start=False,
    )

    apic_password = CustomPasswordField(
        label='APIC PASSWORD',
        default='abc',
        validators=[DataRequired()],
        is_disabled_on_start=False,
    )

    boolean_unchecked = CustomBooleanField(
        label='Import ACI Fabric Devices',
        is_disabled_on_start=False,
    )

    configuration = Configuration(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        required=True,
        coerce=int,
        label='to',
        validators=[],
        is_disabled_on_start=False,
        enable_on_complete=['discover'],
        clear_below_on_change=False,
    )

    discover = CustomSubmitField(
        label='DISCOVER TENANTS',
        is_disabled_on_start=False,
    )
