# Copyright 2019 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import CustomStringField, CustomSubmitField
from . import service_requests_config


class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'configure_service_requests'
    workflow_permission = 'configure_service_requests_page'
    servicenow_url = CustomStringField(
        label='ServiceNow URL',
        default=service_requests_config.servicenow_url,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True,
    )

    servicenow_username = CustomStringField(
        label='ServiceNow User',
        default=service_requests_config.servicenow_username,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True
    )

    servicenow_secret_file = CustomStringField(
        label='ServiceNow Secret file and path',
        default=service_requests_config.servicenow_secret_file,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True
    )

    submit = CustomSubmitField(
        label='Save',
        is_disabled_on_start=False,
        is_disabled_on_error=False
    )