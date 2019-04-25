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
# limitations under the License

# Various Flask framework items.
import os
import sys

from flask import request, url_for, redirect, render_template, flash, g, jsonify
from wtforms.validators import URL, DataRequired
from wtforms import StringField, PasswordField, SubmitField, SelectField

from bluecat.wtform_extensions import GatewayForm

from bluecat import route, util
import config.default_config as config
from main_app import app

from .absorbaroo import Absorbaroo

def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))

class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'absorbaroo'
    workflow_permission = 'absorbaroo_page'

    text=util.get_text(module_path(), config.language)
    invalid_url_message=text['invalid_url_message']
    require_message=text['require_message']

    # Office 365 Pane
    o365_instance = SelectField(
        label=text['label_o365_instance'],
        choices=[
            ('Worldwide', 'Worldwide'),
            ('USGovDoD', 'USGovDoD'),
            ('USGovGCCHigh', 'USGovGCCHigh'),
            ('China', 'China'),
            ('Germany', 'Germany')
        ],
        default='Worldwide'
    )
    o365_client_id = StringField(
        label=text['label_o365_client_id'],
        validators=[DataRequired(message=require_message)]
    )

    # DNS Edge Pane
    edge_url = StringField(
        label=text['label_edge_url'],
        validators=[URL(message=invalid_url_message)],
        render_kw={"placeholder": "https://api-<Edge Instance>.bluec.at"}
    )
    edge_username = StringField(
        label=text['label_edge_username'],
        validators=[DataRequired(message=require_message)]
    )
    edge_password = PasswordField(
        label=text['label_edge_password']
    )
    edge_domainlist = StringField(
        label=text['label_edge_domainlist'],
        validators=[DataRequired(message=require_message)]
    )

    # SDWAN Pane
    sdwan_key = StringField(
        label=text['label_sdwan_key'],
        validators=[DataRequired(message=require_message)]
    )
    sdwan_orgname = StringField(
        label=text['label_sdwan_orgname'],
        validators=[DataRequired(message=require_message)]
    )
    sdwan_tmpname = StringField(
        label=text['label_sdwan_tmpname'],
        validators=[DataRequired(message=require_message)]
    )
    sdwan_delimit_key = StringField(
        label=text['label_sdwan_delimit_key']
    )

    # Execution Pane
    current_version = StringField(
        label=text['label_current_version'],
        render_kw={'readonly': True}
    )
    last_execution = StringField(
        label=text['label_last_execution'],
        render_kw={'readonly': True}
    )
    execution_interval = StringField(
        label=text['label_execution_interval'],
        validators=[DataRequired(message=require_message)]
    )

    submit = SubmitField(label=text['label_submit'])
    execute_now = SubmitField(label=text['label_synchronize_now'])
    clear = SubmitField(label=text['label_clear'])


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/absorbaroo/absorbaroo_endpoint')
@util.workflow_permission_required('absorbaroo_page')
@util.exception_catcher
def absorbaroo_absorbaroo_page():
    form = GenericFormTemplate()
    absorbaroo = Absorbaroo.get_instance()

    value = absorbaroo.get_value('o365_instance')
    if value is not None:
        form.o365_instance.data = value
    value = absorbaroo.get_value('o365_client_id')
    if value is not None:
        form.o365_client_id.data = value

    value = absorbaroo.get_value('edge_url')
    if value is not None:
        form.edge_url.data = value
    value = absorbaroo.get_value('edge_username')
    if value is not None:
        form.edge_username.data = value
    value = absorbaroo.get_value('edge_password')
    if value is not None:
        form.edge_password.data = value
    value = absorbaroo.get_value('edge_domainlist')
    if value is not None:
        form.edge_domainlist.data = value['name']

    value = absorbaroo.get_value('sdwan_key')
    if value is not None:
        form.sdwan_key.data = value
    value = absorbaroo.get_value('sdwan_orgname')
    if value is not None:
        form.sdwan_orgname.data = value
    value = absorbaroo.get_value('sdwan_tmpname')
    if value is not None:
        form.sdwan_tmpname.data = value
    value = absorbaroo.get_value('sdwan_delimit_key')
    if value is not None:
        form.sdwan_delimit_key.data = value

    value = absorbaroo.get_value('current_version')
    if value is not None:
        form.current_version.data = value
    value = absorbaroo.get_value('last_execution')
    if value is not None:
        form.last_execution.data = value
    value = absorbaroo.get_value('execution_interval')
    if value is not None:
        form.execution_interval.data = str(value)

    return render_template(
        'absorbaroo_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/absorbaroo/load_col_model')
@util.workflow_permission_required('absorbaroo_page')
@util.exception_catcher
def load_col_model():
    text=util.get_text(module_path(), config.language)

    nodes = [
        {'index':'name', 'name':'name', 'hidden':True, 'sortable':False},
        {
            'label': text['label_col_name'], 'index':'display_name', 'name':'display_name',
            'width':400, 'sortable':False
        },
        {
            'label': text['label_col_check'], 'index':'check', 'name':'check',
            'width':60, 'align':'center', 'sortable':False,
            'editoptions': { 'value':'True:False'},'formatter':'checkbox'
        }
    ]
    return jsonify(nodes)

@route(app, '/absorbaroo/load_service_areas')
@util.workflow_permission_required('absorbaroo_page')
@util.exception_catcher
def load_service_areas():
    absorbaroo = Absorbaroo.get_instance()
    service_areas = absorbaroo.get_value('o365_service_areas')
    return jsonify(service_areas)

@route(app, '/absorbaroo/submit_service_areas', methods=['POST'])
@util.workflow_permission_required('absorbaroo_page')
@util.exception_catcher
def submit_service_areas():
    service_areas = request.get_json()
    absorbaroo = Absorbaroo.get_instance()
    absorbaroo.set_value('o365_service_areas', service_areas)
    return ""

@route(app, '/absorbaroo/form', methods=['POST'])
@util.workflow_permission_required('absorbaroo_page')
@util.exception_catcher
def absorbaroo_absorbaroo_page_form():
    form = GenericFormTemplate()
    absorbaroo = Absorbaroo.get_instance()
    text=util.get_text(module_path(), config.language)

    if form.validate_on_submit():
        absorbaroo.set_value('o365_instance', form.o365_instance.data)
        absorbaroo.set_value('o365_client_id', form.o365_client_id.data)

        absorbaroo.set_value('edge_url', form.edge_url.data)
        absorbaroo.set_value('edge_username', form.edge_username.data)

        if form.edge_password.data != '':
            absorbaroo.set_value('edge_password', form.edge_password.data)

        domainlist = absorbaroo.get_value('edge_domainlist')
        if domainlist['name'] != form.edge_domainlist.data:
            domainlist['name'] = form.edge_domainlist.data
            domainlist['edge_id'] = ''
            absorbaroo.set_value('edge_domainlist', domainlist)

        absorbaroo.set_value('sdwan_key', form.sdwan_key.data)
        absorbaroo.set_value('sdwan_orgname', form.sdwan_orgname.data)
        absorbaroo.set_value('sdwan_tmpname', form.sdwan_tmpname.data)
        absorbaroo.set_value('sdwan_delimit_key', form.sdwan_delimit_key.data)

        absorbaroo.set_value('execution_interval', int(form.execution_interval.data))

        if form.submit.data:
            absorbaroo.save()
            g.user.logger.info('SAVED')
            flash(text['saved_message'], 'succeed')
        elif form.execute_now.data:
            if absorbaroo.force_synchronize_endpoints():
                flash(text['sychronized_message'], 'succeed')
            else:
                flash(text['failed_message'], 'failed')
        elif form.clear.data:
            if absorbaroo.clear_endpoints():
                flash(text['clear_message'], 'succeed')
            else:
                flash(text['failed_message'], 'failed')
        absorbaroo.register_synchronize_job()
        return redirect(url_for('absorbarooabsorbaroo_absorbaroo_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'absorbaroo_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
