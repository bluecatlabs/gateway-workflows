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

from bluecat import route, util
from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import TableField

import config.default_config as config
from main_app import app

def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))

def get_resource_text():
    return util.get_text(module_path(), config.language)

sql_params = [
    {'id': 'entity', 'table': 'public.entity', 'where': ""},
    {'id': 'ip4b', 'table': 'public.entity', 'where': "WHERE discriminator = 'IP4B'"},
    {'id': 'ip4n', 'table': 'public.entity', 'where': "WHERE discriminator = 'IP4N'"},
    {'id': 'ip4a', 'table': 'public.ipv4_address_basic_view', 'where': ""},
    {'id': 'view', 'table': 'public.entity', 'where': "WHERE discriminator = 'VIEW'"},
    {'id': 'zone', 'table': 'public.entity', 'where': "WHERE discriminator = 'ZONE'"},
    {'id': 'record', 'table': 'public.resource_record_view', 'where': ""},
    {'id': 'mac', 'table': 'public.entity', 'where': "WHERE discriminator = 'MACA'"},
    {'id': 'nusr', 'table': 'public.entity', 'where': "WHERE discriminator = 'NUSR'"},
    {'id': 'gusr', 'table': 'public.entity', 'where': "WHERE discriminator = 'GUSR'"},
    {'id': 'location', 'table': 'public.entity', 'where': "WHERE discriminator = 'LOCATION'"},
]

def load_statistics(text):
    data = []

    db_address = os.environ['BAM_IP']
    connector = psycopg2.connect(host=db_address, database="proteusdb", user="bcreadonly")
    cursor = connector.cursor()

    db_size_sql = "SELECT pg_size_pretty(pg_database_size('proteusdb')) FROM pg_database"
    cursor.execute(db_size_sql)
    result = cursor.fetchall()
    data.append([text['title_db_size'], result[0][0]])

    for sql_param in sql_params:
        sql = "SELECT count(id) FROM %s %s" % (sql_param['table'], sql_param['where'])
        cursor.execute(sql)
        result = cursor.fetchall()
        data.append([text['title_%s_count' % sql_param['id']], '{:,}'.format(int(result[0][0]))])

    cursor.close()
    connector.close()
    return data

def table_features():
    """Returns table formatted data for display in the TableField component"""
    # pylint: disable=unused-argument


    text = get_resource_text()
    data = load_statistics(text)

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
        'lengthChange': False,
        'data': data
    }

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
        table_features=table_features(),
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
