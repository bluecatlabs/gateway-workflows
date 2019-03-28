# Copyright 2018 BlueCat Networks. All rights reserved.
"""
Workflow form template
"""
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import TableField, PlainHTML

from .component_logic import raw_table_data


class GenericFormTemplate(GatewayForm):
    workflow_name = 'manage_service_requests'
    workflow_permission = 'manage_service_requests_page'

    report_div = PlainHTML('<div id="report_div"><a href="/manage_service_requests/generate_service_requests_report" target="_blank">Export Service Requests report as CSV</a> - This report will generate a CSV with a list of all the service requests(open and closed) and match the information within BlueCat to give the most up-to-date information<br>'
                           '</div><br>')

    ticket_table = TableField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        data_function=raw_table_data,
        table_features={
            'searching': True,
            'paging': True,
            'ordering': True,
            'info': True,
            'lengthChange': True,
            'scrollX': True,
            'pageLength': 10,
            'columnDefs': [
                {
                    'targets': [5],
                    'render': ''
                }],
            'language': {
                "lengthMenu": 'Display Entries<select>' +
                              '<option value="10">10</option>' +
                              '<option value="25">25</option>' +
                              '<option value="100">100</option>' +
                              '</select>'
            },
        },
    )
