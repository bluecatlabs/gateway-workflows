# Copyright 2017 BlueCat Networks (USA) Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By: BlueCat Networks
# Date: 07-12-17
# Gateway Version: 17.12.1
# Description: Example Gateway workflows

# Various Flask framework items.
import os
import sys

import importlib

from flask import url_for, redirect, render_template, flash, g, request

from bluecat import route, util
import config.default_config as config
from main_app import app
from .delete_ip4_address_example_form import GenericFormTemplate

# Import the common; this type of import is requried due to a space in the name
ip4_example_common = importlib.import_module("bluecat_portal.workflows.Examples.IPv4 Address.ip4_example_common")


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(unicode(__file__, encoding)))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/delete_ip4_address_example/delete_ip4_address_example_endpoint')
@util.workflow_permission_required('delete_ip4_address_example_page')
@util.exception_catcher
def delete_ip4_address_example_delete_ip4_address_example_page():
    form = GenericFormTemplate()
    return render_template('delete_ip4_address_example_page.html', form=form, text=util.get_text(module_path(), config.language), options=g.user.get_options())


@route(app, '/delete_ip4_address_example/form', methods=['POST'])
@util.workflow_permission_required('delete_ip4_address_example_page')
@util.exception_catcher
def delete_ip4_address_example_delete_ip4_address_example_page_form():
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    if form.validate_on_submit():
        try:
            # Retrieve form attributes
            configuration = g.user.get_api().get_entity_by_id(form.configuration.data)

            # Retrieve IP4 Object
            ip4_object = configuration.get_ip4_address(util.safe_str(request.form.get('ip4_address', '')))

            # Retrieve alias_record attributes for flash message
            ip4_address = util.safe_str(ip4_object.get_property('address'))
            ip4_id = util.safe_str(ip4_object.get_id())

            # Delete IP4 Object
            ip4_object.delete()

            # Put form processing code here
            g.user.logger.info('Success - IP4 Object ' + ip4_address + ' Deleted with Object ID: ' + ip4_id)
            flash('Success - IP4 Object ' + ip4_address + ' Deleted with Object ID: ' + ip4_id, 'succeed')
            return redirect(url_for('delete_ip4_address_exampledelete_ip4_address_example_delete_ip4_address_example_page'))
        except Exception as e:
            flash(util.safe_str(e))
            # Log error and render workflow page
            g.user.logger.warning('%s' % util.safe_str(e), msg_type=g.user.logger.EXCEPTION)
            return render_template('delete_ip4_address_example_page.html',
                                   form=form,
                                   text=util.get_text(module_path(), config.language),
                                   options=g.user.get_options())
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template('delete_ip4_address_example_page.html',
                               form=form,
                               text=util.get_text(module_path(), config.language),
                               options=g.user.get_options())
