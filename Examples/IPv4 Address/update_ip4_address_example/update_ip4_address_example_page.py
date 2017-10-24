# Copyright 2017 BlueCat Networks. All rights reserved.

# Various Flask framework items.
import os
import sys
import importlib

from flask import url_for, redirect, render_template, flash, g, request

from bluecat import route, util
import config.default_config as config
from main_app import app
from .update_ip4_address_example_form import GenericFormTemplate
from bluecat.api_exception import APIException

# Import the common; this type of import is requried due to a space in the name
ip4_example_common = importlib.import_module("bluecat_portal.workflows.Examples.IPv4 Address.ip4_example_common")


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(unicode(__file__, encoding)))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/update_ip4_address_example/update_ip4_address_example_endpoint')
@util.workflow_permission_required('update_ip4_address_example_page')
@util.exception_catcher
def update_ip4_address_example_update_ip4_address_example_page():
    form = GenericFormTemplate()
    return render_template('update_ip4_address_example_page.html', form=form, text=util.get_text(module_path(), config.language), options=g.user.get_options())


@route(app, '/update_ip4_address_example/form', methods=['POST'])
@util.workflow_permission_required('update_ip4_address_example_page')
@util.exception_catcher
def update_ip4_address_example_update_ip4_address_example_page_form():
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    if form.validate_on_submit():
        try:
            # Retrieve form attributes
            configuration = g.user.get_api().get_entity_by_id(form.configuration.data)

            # Retrieve the IP4 address object
            ip4_address = configuration.get_ip4_address(request.form.get('ip4_address', ''))

            # Update the form name and mac address properties
            ip4_address.set_name(form.description.data)
            ip4_address.set_property('macAddress', form.mac_address.data)
            ip4_address.update()

            # Put form processing code here
            g.user.logger.info('Success - IP4 Address Modified - Object ID: ' + util.safe_str(ip4_address.get_id()))
            flash('Success - IP4 Address Modified - Object ID: ' + util.safe_str(ip4_address.get_id()), 'succeed')
            return redirect(url_for('update_ip4_address_exampleupdate_ip4_address_example_update_ip4_address_example_page'))
        except APIException as e:
            flash(util.safe_str(e))
            # Log error and render workflow page
            g.user.logger.warning('%s' % util.safe_str(e), msg_type=g.user.logger.EXCEPTION)
            return render_template('update_ip4_address_example_page.html',
                                   form=form,
                                   text=util.get_text(module_path(), config.language),
                                   options=g.user.get_options())
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template('update_ip4_address_example_page.html',
                               form=form,
                               text=util.get_text(module_path(), config.language),
                               options=g.user.get_options())
