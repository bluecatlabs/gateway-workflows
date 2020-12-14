# Copyright 2020 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""
import datetime

from wtforms import StringField, PasswordField, FileField
from wtforms import BooleanField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Email, MacAddress, URL
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import Configuration, CustomStringField, IP4Address, CustomSubmitField, TableField
from .edge_create_internal_ns_wtform_fields import EdgeNamespaces


class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'edge_create_internal_ns'
    workflow_permission = 'edge_create_internal_ns_page'
    domainlist_name = CustomStringField(
        label='Domain List Name',
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=True,
    )
    domainlist_desc = CustomStringField(
        label='Domain List Description',
        is_disabled_on_start=False,
        is_disabled_on_error=False,
        required=False,
    )
    sourceType = CustomStringField(
        label='Domain List Type',
        default='user',
        is_disabled_on_start=True,
        is_disabled_on_error=True,
        required=True,
    )

    namespaces = EdgeNamespaces(
        label='Edge Namespaces',
        is_disabled_on_start=False,
        workflow_name = workflow_name,
        permissions=workflow_permission
    )

    submit = CustomSubmitField(
        label='Submit',
        is_disabled_on_start=False
    )
