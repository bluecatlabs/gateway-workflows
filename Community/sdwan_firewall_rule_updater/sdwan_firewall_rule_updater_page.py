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
from wtforms import StringField, PasswordField, SubmitField

from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import CustomStringField, CustomSubmitField

from bluecat import route, util
import config.default_config as config
from main_app import app

from .fwrl_updater import FWRLUpdater

def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))

class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'sdwan_firewall_rule_updater'
    workflow_permission = 'sdwan_firewall_rule_updater_page'

    text=util.get_text(module_path(), config.language)
    invalid_url_message=text['invalid_url_message']
    require_message=text['require_message']

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
@route(app, '/sdwan_firewall_rule_updater/sdwan_firewall_rule_updater_endpoint')
@util.workflow_permission_required('sdwan_firewall_rule_updater_page')
@util.exception_catcher
def sdwan_firewall_rule_updater_sdwan_firewall_rule_updater_page():
    form = GenericFormTemplate()
    updater = FWRLUpdater.get_instance()

    value = updater.get_value('edge_url')
    if value is not None:
        form.edge_url.data = value
    value = updater.get_value('edge_username')
    if value is not None:
        form.edge_username.data = value
    value = updater.get_value('edge_password')
    if value is not None:
        form.edge_password.data = value

    value = updater.get_value('sdwan_key')
    if value is not None:
        form.sdwan_key.data = value
    value = updater.get_value('sdwan_orgname')
    if value is not None:
        form.sdwan_orgname.data = value
    value = updater.get_value('sdwan_tmpname')
    if value is not None:
        form.sdwan_tmpname.data = value
    value = updater.get_value('sdwan_delimit_key')
    if value is not None:
        form.sdwan_delimit_key.data = value

    value = updater.get_value('last_execution')
    if value is not None:
        form.last_execution.data = value
    value = updater.get_value('execution_interval')
    if value is not None:
        form.execution_interval.data = str(value)

    return render_template(
        'sdwan_firewall_rule_updater_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/sdwan_firewall_rule_updater/load_col_model')
@util.workflow_permission_required('sdwan_firewall_rule_updater_page')
@util.exception_catcher
def load_col_model():
    text=util.get_text(module_path(), config.language)

    nodes = [
        {
            'label': text['label_col_name'], 'index':'name', 'name':'name',
            'width':200, 'sortable':False
        },
        {
            'label': text['label_col_port'], 'index':'port', 'name':'port',
            'width':80, 'align':'center', 'sortable':False
        },
        {
            'label': text['label_col_protocol'], 'index':'protocol', 'name':'protocol',
            'width':80, 'align':'center', 'sortable':False
        },
        {
            'label': text['label_col_fqdn'], 'index':'fqdn', 'name':'fqdn',
            'width':60, 'align':'center', 'sortable':False,
            'editoptions': { 'value':'True:False'},'formatter':'checkbox'
        },
        {'index':'edge_id', 'name':'edge_id', 'hidden':True, 'sortable':False},
        {'index':'hash_value', 'name':'hash_value', 'hidden':True, 'sortable':False}
    ]
    return jsonify(nodes)

@route(app, '/sdwan_firewall_rule_updater/load_domain_lists')
@util.workflow_permission_required('sdwan_firewall_rule_updater_page')
@util.exception_catcher
def load_domain_lists():
    updater = FWRLUpdater.get_instance()
    domainlists = updater.get_value('edge_domainlists')
    return jsonify(domainlists)

@route(app, '/sdwan_firewall_rule_updater/submit_domain_lists', methods=['POST'])
@util.workflow_permission_required('sdwan_firewall_rule_updater_page')
@util.exception_catcher
def submit_domain_lists():
    domain_lists = request.get_json()
    updater = FWRLUpdater.get_instance()
    updater.set_value('edge_domainlists', domain_lists)
    return ""

@route(app, '/sdwan_firewall_rule_updater/form', methods=['POST'])
@util.workflow_permission_required('sdwan_firewall_rule_updater_page')
@util.exception_catcher
def sdwan_firewall_rule_updater_sdwan_firewall_rule_updater_page_form():
    form = GenericFormTemplate()
    updater = FWRLUpdater.get_instance()
    text=util.get_text(module_path(), config.language)

    if form.validate_on_submit():
        updater.set_value('edge_url', form.edge_url.data)
        updater.set_value('edge_username', form.edge_username.data)
        if form.edge_password.data != '':
            updater.set_value('edge_password', form.edge_password.data)

        updater.set_value('sdwan_key', form.sdwan_key.data)
        updater.set_value('sdwan_orgname', form.sdwan_orgname.data)
        updater.set_value('sdwan_tmpname', form.sdwan_tmpname.data)
        updater.set_value('sdwan_delimit_key', form.sdwan_delimit_key.data)

        updater.set_value('execution_interval', int(form.execution_interval.data))
        updater.save()
        g.user.logger.info('SAVED')

        if form.submit.data:
            flash(text['saved_message'], 'succeed')
        elif form.execute_now.data:
            if updater.force_synchronize_domainlists():
                flash(text['sychronized_message'], 'succeed')
            else:
                flash(text['failed_message'], 'failed')
        elif form.clear.data:
            if updater.clear_domainlists():
                flash(text['clear_message'], 'succeed')
            else:
                flash(text['failed_message'], 'failed')
        updater.register_synchronize_job()
        return redirect(url_for('sdwan_firewall_rule_updatersdwan_firewall_rule_updater_sdwan_firewall_rule_updater_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'sdwan_firewall_rule_updater_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
