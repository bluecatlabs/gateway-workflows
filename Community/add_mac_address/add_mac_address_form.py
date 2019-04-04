# Copyright 2019 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""
from wtforms.validators import MacAddress
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import Configuration, CustomStringField, CustomBooleanField, CustomSubmitField
from .add_mac_address_wtform_fields import MACPool


class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'add_mac_address'
    workflow_permission = 'add_mac_address_page'

    configuration = Configuration(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Configuration',
        required=True,
        coerce=int,
        is_disabled_on_start=False,
    )

    mac_address = CustomStringField(
        label='MAC Address',
        is_disabled_on_start=False,
        validators=[MacAddress()],
        required=True
    )

    mac_address_name = CustomStringField(
        label='MAC Address Name',
        is_disabled_on_start=False,
        required=True
    )

    mac_pool_boolean = CustomBooleanField(
        label='Add to MAC Pool',
        is_disabled_on_start=False
    )

    mac_pool = MACPool(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='MAC Pool',
        is_disabled_on_start=False
    )

    submit = CustomSubmitField(
        label='Submit',
        is_disabled_on_start=False
    )
