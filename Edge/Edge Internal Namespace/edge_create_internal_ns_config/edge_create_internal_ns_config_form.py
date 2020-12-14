# Copyright 2020 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""

from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import CustomStringField, CustomSubmitField
from . import edge_create_internal_ns_configuration


class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'edge_create_internal_ns_config'
    workflow_permission = 'edge_umbrella_domain_list_config_page'
    default_configuration = CustomStringField(
        label='Default Configuration',
        default=edge_create_internal_ns_configuration.default_configuration,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True,
    )
    default_view = CustomStringField(
        label='Default DNS View',
        default=edge_create_internal_ns_configuration.default_view,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True,
    )
    edge_url = CustomStringField(
        label='Edge URL',
        default=edge_create_internal_ns_configuration.edge_url,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True,
    )
    domain_list_file = CustomStringField(
        label='Domain List File',
        default=edge_create_internal_ns_configuration.domain_list_file,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True,
    )
    client_id = CustomStringField(
        label='Edge Client ID',
        default=edge_create_internal_ns_configuration.client_id,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True,
    )
    clientSecret = CustomStringField(
        label='Edge Client Secret',
        default=edge_create_internal_ns_configuration.clientSecret,
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True,
    )
    submit = CustomSubmitField(
        label='Save',
        is_disabled_on_start=False,
        is_disabled_on_error=False
    )
