# Copyright 2019 BlueCat Networks. All rights reserved.

# Various Flask framework items.
import os
import sys


from flask import url_for, redirect, render_template, flash, g, request, make_response

from bluecat import route, util
import config.default_config as config
from main_app import app
from .bulk_record_export_form import GenericFormTemplate

def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/bulk_record_export/bulk_record_export_endpoint')
@util.workflow_permission_required('bulk_record_export_page')
@util.exception_catcher
def bulk_record_export_bulk_record_export_page():
    form = GenericFormTemplate()
    return render_template(
        'bulk_record_export_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/bulk_record_export/form', methods=['POST'])
@util.workflow_permission_required('bulk_record_export_page')
@util.exception_catcher
def bulk_record_export_bulk_record_export_page_form():
    form = GenericFormTemplate()

    if form.validate_on_submit():
        g.user.logger.info('SUCCESS')
        flash('success', 'succeed')
        return redirect(url_for('bulk_record_exportbulk_record_export_bulk_record_export_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'bulk_record_export_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )



