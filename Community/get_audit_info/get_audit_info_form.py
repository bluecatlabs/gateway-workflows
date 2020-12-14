# Copyright 2020 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""
import datetime

from wtforms import StringField, PasswordField, FileField
from wtforms import BooleanField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Email, MacAddress, URL
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import Configuration, CustomStringField, IP4Address, CustomSelectField, CustomSearchButtonField, TableField
from .get_audit_infot_logic import find_objects_by_type_endpoint, raw_table_data


class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'get_audit_info'
    workflow_permission = 'get_audit_info_page'
    interval = CustomSelectField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Time Interval',
        choices=[('Please Select', 'Please Select'), ('1 hours', '1 hours'), ('2 hours', '2 hours'), ('5 hours', '5 hours'), ('12 hours', '12 hours'), ('24 hours', '24 hours')],
        required=True,
        enable_on_complete=['search'],
        is_disabled_on_start=False
    )

    search = CustomSearchButtonField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        default='Search Objects',
        inputs={'interval': 'interval'},
        server_side_method=find_objects_by_type_endpoint,
        display_message=True,
        on_complete=['call_server_table'],
        enable_on_complete=['submit'],
        is_disabled_on_start=True
    )

    server_table = TableField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='',
        data_function=raw_table_data,
        table_features={
            'searching': True,
            'paging': True,
            'ordering': True,
            'info': True
        },
        inputs={'ip4_network': 'ip4_network'}
    )