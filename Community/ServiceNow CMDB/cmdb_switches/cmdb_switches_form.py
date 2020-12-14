# Copyright 2020 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""

from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import TableField, PlainHTML
from .cmdb_switches_logic import raw_table_data


class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'cmdb_switches'
    workflow_permission = 'cmdb_switches_page'
    switches_table = TableField(
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

