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
import sys
import codecs

from flask import url_for, redirect, render_template, flash, g

from bluecat import route, util
import config.default_config as config
from main_app import app
from .network_manager_form import GenericFormTemplate



def module_path():
    return os.path.dirname(os.path.abspath(str(__file__)))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/network_manager/network_manager_endpoint')
@util.workflow_permission_required('network_manager_page')
@util.exception_catcher
def network_manager_network_manager_page():
    form = GenericFormTemplate()
    user = g.user._username

    bv = g.user.get_api().get_by_object_types(user, ['IP4Block'])
    has_block=False
    for b in bv:
        has_block = True

    if has_block == False:
        flash("You don't have any network space allocated to your group")
    return render_template(
        'network_manager_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/network_manager/form', methods=['POST'])
@util.workflow_permission_required('network_manager_page')
@util.exception_catcher
def network_manager_network_manager_page_form():
    form = GenericFormTemplate()
    if form.validate_on_submit():
        user = g.user._username
        bv = g.user.get_api().get_by_object_types(user, ['IP4Block'])
        for b in bv:
            block = b
            break
        else:
            flash("This doesn't work, you have no block.")
            app.logger.error("This doesn't work, you have no block.")
        n = block.get_next_available_ip_range(form.network_size.data, "IP4Network")
        n.name = "%s | %s" % (form.network_location.data, form.network_name.data)
        n.update()
        # Put form processing code here
        g.user.logger.info('SUCCESS')
        flash('Created network %s with %s addresses at %s'%(n.name, form.network_size.data, n.get_property("CIDR")), 'succeed')
        return redirect(url_for('network_managernetwork_manager_network_manager_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'network_manager_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
