# Copyright 2020 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""
import datetime

from wtforms import StringField, PasswordField, FileField
from wtforms import BooleanField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Email, MacAddress, URL
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import Configuration, CustomStringField, IP4Address, TableField
from .cmdb_router_logic import raw_table_data

class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'cmdb_routers'
    workflow_permission = 'cmdb_routers_page'
    router_table = TableField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        data_function=raw_table_data,
        label='',
        table_features={
            'searching': True,
            'paging': True,
            'ordering': True,
        },
    )
