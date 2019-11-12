# Copyright 2019 BlueCat Networks. All rights reserved.

# Various Flask framework items.
import os
import sys

from flask import url_for, redirect, render_template, flash, g

import config.default_config as config
from bluecat import route, util
from main_app import app
from .move_to_bluecatgateway_udf_form import GenericFormTemplate


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/move_to_bluecatgateway_udf/move_to_bluecatgateway_udf_endpoint')
@util.workflow_permission_required('move_to_bluecatgateway_udf_page')
@util.exception_catcher
def move_to_bluecatgateway_udf_move_to_bluecatgateway_udf_page():
    form = GenericFormTemplate()
    return render_template(
        'move_to_bluecatgateway_udf_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/move_to_bluecatgateway_udf/form', methods=['POST'])
@util.workflow_permission_required('move_to_bluecatgateway_udf_page')
@util.exception_catcher
def move_to_bluecatgateway_udf_move_to_bluecatgateway_udf_page_form():
    form = GenericFormTemplate()

    if form.validate_on_submit():
        # Get all users in Address Manager
        users = g.user.get_api().get_by_object_types('*', 'User')

        # Loop though all users and set the BlueCatGateway based off what's set for PortalGroup
        usr_count = update_count =0
        for user in users:
            usr_count += 1
            if user.get_property('PortalGroup'):
                user.set_property('BlueCatGateway', user.get_property('PortalGroup'))
                user.update()
                update_count += 1
                g.user.logger.info(user.name + ' BlueCatGateway UDF updated to: ' + user.get_property('PortalGroup'))
            else:
                g.user.logger.info(user.name + ' Did not have PortalGroup value,  BlueCatGateway not updated')

        # Put form processing code here
        g.user.logger.info('SUCCESS')
        flash('success', 'succeed')
        return redirect(url_for('move_to_bluecatgateway_udfmove_to_bluecatgateway_udf_move_to_bluecatgateway_udf_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'move_to_bluecatgateway_udf_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
