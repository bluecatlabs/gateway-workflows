# Copyright 2019 BlueCat Networks (USA) Inc. and its affiliates
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
import os
from bluecat_portal.customizations.tools import tools
from flask import url_for, redirect, render_template, flash, g, send_from_directory
#from xlrd import open_workbook
from bluecat import route, util
import config.default_config as config
from main_app import app
from .bulk_form import GenericFormTemplate
from .bulk_action import bulk_handler

def module_path():
    return os.path.dirname(os.path.abspath(__file__))

supported_file_types = ('csv')
dir_path = os.path.dirname(os.path.realpath(__file__))

@route(app, '/bulk/bulk_import')
@util.workflow_permission_required('bulk')
@util.exception_catcher
def bulk_bulk():
    form = GenericFormTemplate()
    form.configuration.choices = util.get_configurations(default_val=True)
    return render_template(
        'bulk.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/bulk/download/<file>')
@util.workflow_permission_required('bulk')
@util.exception_catcher
def download(file):
    return send_from_directory(dir_path+'/file_repository/downloads/', file)


@route(app, '/bulk/upload', methods=['POST'])
@util.workflow_permission_required('bulk')
@util.exception_catcher
def upload():
    form = GenericFormTemplate()
    file = form.file.data
    if is_supported(file.filename) is False:
        flash('Unsupported file type')
        return redirect(url_for('bulkbulk_bulk'))

    try:
        file = tools.save_file(file, dir_path+'/file_repository/uploads/')
    except:
        g.user.logger.error("Unable to save file")
        flash('Unable to save file')
        return redirect(url_for('bulkbulk_bulk'))
    try:
        if file.split(".")[-1] not in ('csv'):
            """wb = open_workbook(file)
            contents = []
            if wb.nsheets > 0:
                sheet = wb.sheet_by_index(0)
                for row_index in range(0, sheet.nrows):
                    row = [int(cell.value) if isinstance(cell.value, float) else str(cell.value)
                           for cell in sheet.row(row_index)]
                    contents.append(",".join(row))
                contents = "\n".join(contents)"""
            print("Not supported")
        else:
            try:
                with open(file) as f:
                    contents = f.read().decode("utf-8-sig").encode("utf-8")
            except Exception as e:
                try:
                    with open(file) as f:
                        contents = f.read()
                except:
                    raise e

        contents_as_dict = tools.parse_csv_to_dict(contents)
    except Exception as e:
        g.user.logger.error(str(e))
        g.user.logger.error("Unable to parse file")
        flash('Unable to parse file')
        return redirect(url_for('bulkbulk_bulk'))

    parser = bulk_handler(g, form)
    for key, value in list(contents_as_dict.items()):
        parser.handle_row(key, value)

    status, message = parser.go_no_go()
    if message != "":
        flash(message)
    if status is False:
        return redirect(url_for('bulkbulk_bulk'))

    return parser.return_action()


def is_supported(filename):
    bits = filename.split('.')
    if len(bits) > 1:
        return bits[-1] in supported_file_types
    else:
        return False
