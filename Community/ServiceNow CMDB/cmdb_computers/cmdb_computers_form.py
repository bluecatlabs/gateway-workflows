# Copyright 2019 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import Configuration, CustomStringField, IP4Address, TableField
from .cmdb_computer_logic import raw_table_data


class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'cmdb_computers'
    workflow_permission = 'cmdb_computers_page'
    computer_table = TableField(
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