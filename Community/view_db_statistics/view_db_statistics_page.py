# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Various Flask framework items.
import os
import sys
import codecs
import psycopg2

from flask import url_for, redirect, render_template, flash, g
from flask import jsonify
from flask import request

from bluecat import route, util
from bluecat.constants import BAMStats
from bluecat.util import rest_exception_catcher
from bluecat.util import rest_workflow_permission_required
from bluecat.server_endpoints import empty_decorator
from bluecat.server_endpoints import get_result_template
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import TableField

import config.default_config as config
from main_app import app

def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))

def get_resource_text():
    return util.get_text(module_path(), config.language)

stats_params = [
    {'id': 'db_size', 'indicator': BAMStats.DB_SIZE},
    {'id': 'entity_count', 'indicator': BAMStats.ENTITY_COUNT},
    {'id': 'ip4b_count', 'indicator': BAMStats.IP4_BLOCK_COUNT},
    {'id': 'ip4n_count', 'indicator': BAMStats.IP4_NETWORK_COUNT},
    {'id': 'ip4a_count', 'indicator': BAMStats.IP4_ADDRESS_COUNT},
    {'id': 'view_count', 'indicator': BAMStats.VIEW_COUNT},
    {'id': 'zone_count', 'indicator': BAMStats.ZONE_COUNT},
    {'id': 'record_count', 'indicator': BAMStats.RESOURCE_RECORD_COUNT},
    {'id': 'mac_count', 'indicator': BAMStats.MAC_ADDRESS_COUNT},
    {'id': 'nusr_count', 'indicator': BAMStats.USER_COUNT},
    {'id': 'gusr_count', 'indicator': BAMStats.GROUP_COUNT},
    {'id': 'location_count', 'indicator': BAMStats.LOCATION_COUNT},
]
def table_features():
    """Returns table formatted data for display in the TableField component"""
    # pylint: disable=unused-argument
    text = get_resource_text()

    return {
        'columns': [
            {'title': text['title_title']},
            {'title': text['title_value']}
        ],
        'columnDefs': [
            {'className': 'dt-right', 'targets': [1]}
        ],
        'searching': False,
        'ordering': False,
        'paging': False,
        'info': False,
        'lengthChange': False
    }


def load_statistics(api, text):
    indicators = []
    for param in stats_params:
        indicators.append(param['indicator'])
    stats = api.get_bam_db_stats(indicators)

    data = table_features()
    data['data'] = []
    for param in stats_params:
        data['data'].append([text['title_%s' % param['id']], stats[param['indicator']]])
    return data

def server_table_data_endpoint(workflow_name, element_id, permissions, result_decorator=None):
    """Endpoint for server table data"""
    # pylint: disable=unused-argument
    endpoint = 'server_table_data'
    function_endpoint = '%sserver_table_data' % workflow_name
    view_function = app.view_functions.get(function_endpoint)
    if view_function is not None:
        return endpoint
    if not result_decorator:
        result_decorator = empty_decorator

    g.user.logger.info('Creating endpoint %s', endpoint)

    @route(app, '/%s/%s' % (workflow_name, endpoint), methods=['POST'])
    @rest_workflow_permission_required(permissions)
    @rest_exception_catcher
    # pylint: disable=unused-variable
    def server_table_data():
        """Retrieve server side table data"""
        # pylint: disable=broad-except
        print('Server Table Data is Called!!!!')
        try:
            text = get_resource_text()
            data = load_statistics(g.user.get_api(), text)
            result = get_result_template()

            result['status'] = 'SUCCESS'
            result['data'] = {"table_field": data}
            return jsonify(result_decorator(result))

        except Exception as e:
            result = get_result_template()
            result['status'] = 'FAIL'
            result['message'] = str(e)
            return jsonify(result_decorator(result))

    return endpoint

class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'view_db_statistics'
    workflow_permission = 'view_db_statistics_page'

    text = get_resource_text()
    output_table = TableField(
        workflow_name=workflow_name,
        permissions=workflow_permission,
        label=text['label_list'],
        table_features={
            'columns': [
                {'title': text['title_title']},
                {'title': text['title_value']}
            ],
            'columnDefs': [
                {'className': 'dt-right', 'targets': [1]}
            ],
            'searching': False,
            'ordering': False,
            'paging': False,
            'info': False,
            'lengthChange': False
        },
        server_side_method=server_table_data_endpoint,
        is_disabled_on_start=False
    )

# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/view_db_statistics/view_db_statistics_endpoint')
@util.workflow_permission_required('view_db_statistics_page')
@util.exception_catcher
def view_db_statistics_view_db_statistics_page():
    form = GenericFormTemplate()

    return render_template(
        'view_db_statistics_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )
