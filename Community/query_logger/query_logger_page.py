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

from flask import url_for, redirect, render_template, flash, g
from wtforms.validators import DataRequired, IPAddress, URL, NumberRange
from wtforms import SubmitField

from bluecat.wtform_extensions import GatewayForm
from bluecat.wtform_fields import CustomStringField
from bluecat import route, util
import config.default_config as config
from main_app import app

from .query_logger import QueryLogger

def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))

class GenericFormTemplate(GatewayForm):
    """
    Generic form Template

    Note:
        When updating the form, remember to make the corresponding changes to the workflow pages
    """
    workflow_name = 'query_logger'
    workflow_permission = 'query_logger_page'

    text=util.get_text(module_path(), config.language)
    invalid_url_message=text['invalid_url_message']
    require_message=text['require_message']

    edge_url = CustomStringField(
        label=text['label_edge_url'],
        is_disabled_on_start=False,
        validators=[DataRequired(message=require_message), URL(message=invalid_url_message)],
        render_kw={"placeholder": "https://api-<Edge Instance>.bluec.at"}
    )

    edge_token = CustomStringField(
        label=text['label_edge_token'],
        is_disabled_on_start=False,
        validators=[DataRequired(message=require_message)]
    )

    syslog_server = CustomStringField(
        label=text['label_syslog_server'],
        is_disabled_on_start=False,
        validators=[DataRequired(message=require_message), IPAddress()]
    )

    poll_interval = CustomStringField(
        label=text['label_poll_interval'],
        is_disabled_on_start=False,
        validators=[DataRequired(message=require_message)]
    )

    submit = SubmitField(label=text['label_submit'])


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/query_logger/query_logger_endpoint')
@util.workflow_permission_required('query_logger_page')
@util.exception_catcher
def query_logger_query_logger_page():
    form = GenericFormTemplate()

    query_logger = QueryLogger.get_instance(debug=True)
    form.edge_url.data = query_logger.get_value('edge', 'url')
    form.edge_token.data = query_logger.get_value('edge', 'token')
    form.syslog_server.data = query_logger.get_value('datalog', 'server')
    form.poll_interval.data = query_logger.get_value('poll', 'interval')

    return render_template(
        'query_logger_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/query_logger/form', methods=['POST'])
@util.workflow_permission_required('query_logger_page')
@util.exception_catcher
def query_logger_query_logger_page_form():
    form = GenericFormTemplate()
    if form.validate_on_submit():
        text=util.get_text(module_path(), config.language)
        query_logger = QueryLogger.get_instance(debug=True)

        query_logger.set_value('edge', 'url', form.edge_url.data)
        query_logger.set_value('edge', 'token', form.edge_token.data)
        query_logger.set_value('datalog', 'server', form.syslog_server.data)
        query_logger.set_value('poll', 'interval', int(form.poll_interval.data))

        query_logger.save()
        query_logger.register_job()

        # Put form processing code here
        g.user.logger.info('SAVED')
        flash(text['saved_message'], 'succeed')

        return redirect(url_for('query_loggerquery_logger_query_logger_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'query_logger_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
