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

import os
from flask import url_for, redirect, render_template, flash, g
from bluecat import route, util
import config.default_config as config
from main_app import app
from .hello_edge_form import EdgeForm
from bluecat_portal.customizations.edge import edge

def module_path():
    return os.path.dirname(os.path.abspath(__file__))


@route(app, '/hello_edge/hello_edge')
@util.workflow_permission_required('hello_edge_page')
@util.exception_catcher
def hello_edge_hello_edge_page():
    form = EdgeForm()
    return render_template(
        'hello_edge_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )


@route(app, '/hello_edge/form', methods=['POST'])
@util.workflow_permission_required('hello_edge_page')
@util.exception_catcher
def hello_edge_hello_edge_page_form():
    form = EdgeForm()

    if form.validate_on_submit():

        edge_session = edge(form.edge.data, form.client.data, form.client_secret.data, app.logger)
        if edge_session.get_session_status() is False:
            app.logger.error("We were unable to contact Edge")
            flash('We were unable to contact Edge')
        else:
            app.logger.error("Contacted the Edge")
            flash('Hello from the Edge!', 'succeed')
            flash('')
            flash('here are your first ten lists', 'succeed')
            flash('')
            flash('')
            count = 0
            for s in edge_session.list_dl():
                flash('%s: %s' %(s['name'], s['domainCount']),'succeed')
                count += 1
                print(count)
                if count >= 9:
                    break



        return redirect(url_for('hello_edgehello_edge_hello_edge_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'hello_edge_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
