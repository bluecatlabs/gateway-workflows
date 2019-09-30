# Copyright 2019 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""
import datetime

from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import TableField, CustomSearchButtonField
from .bulk_record_export_wtform_fields import IP4Network
from .bulk_record_export_logic import raw_table_data, find_objects_by_type_endpoint

class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'bulk_record_export'
    workflow_permission = 'bulk_record_export_page'

    ip4_network = IP4Network(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label='Network',
        required=True,
        one_off=False,
        enable_on_complete=['search'],
        is_disabled_on_start=False
    )

    search = CustomSearchButtonField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        default='Search Objects',
        inputs={'ip4_network': 'ip4_network'},
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
