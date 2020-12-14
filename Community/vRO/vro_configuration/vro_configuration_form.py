# Copyright 2020 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import CustomStringField, CustomSubmitField, CustomSelectField
from . import vro_config

class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'vro_configuration'
    workflow_permission = 'vro_configuration_page'
    default_configuration = CustomStringField(
        label='Default Configuration',
        default=vro_config.default_configuration,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True
    )
    default_view = CustomStringField(
        label='vRO Default DNS View',
        default=vro_config.default_view,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True
    )
    default_zone = CustomStringField(
        label='vRO Default Zone',
        default=vro_config.default_zone,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True
    )
    default_reverse_flag = CustomStringField(
        label='vRO Create PTR Record',
        default=vro_config.default_reverse_flag,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True
    )

    submit = CustomSubmitField(
        label='Save',
        is_disabled_on_start=False,
        is_disabled_on_error=False
    )