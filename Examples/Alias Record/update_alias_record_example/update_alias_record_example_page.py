# Copyright 2017 BlueCat Networks. All rights reserved.

# Various Flask framework items.
import os
import sys

from flask import url_for, redirect, render_template, flash, g, request

from bluecat import route, util
import config.default_config as config
from main_app import app
from .update_alias_record_example_form import GenericFormTemplate


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(unicode(__file__, encoding)))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/update_alias_record_example/update_alias_record_example_endpoint')
@util.workflow_permission_required('update_alias_record_example_page')
@util.exception_catcher
def update_alias_record_example_update_alias_record_example_page():
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations(default_val=True)
    return render_template('update_alias_record_example_page.html', form=form, text=util.get_text(module_path(), config.language),
                           options=g.user.get_options())


@route(app, '/update_alias_record_example/form', methods=['POST'])
@util.workflow_permission_required('update_alias_record_example_page')
@util.exception_catcher
def update_alias_record_example_update_alias_record_example_page_form():
    form = GenericFormTemplate()
    # Remove this line if your workflow does not need to select a configuration
    form.configuration.choices = util.get_configurations()
    if form.validate_on_submit():
        try:
            # Retrieve form attributes and declare variables
            configuration = g.user.get_api().get_entity_by_id(form.configuration.data)
            view = configuration.get_view(request.form['view'])

            # Retrieve alias record
            alias_record = view.get_alias_record(request.form['alias_record'] + '.' + request.form['zone'])

            # Update the alias record's name and linkedRecordName
            alias_record.set_name(form.alias_name.data)
            alias_record.set_property('linkedRecordName', request.form['linked_record'] + '.' + request.form['linked_record_zone'])
            alias_record.update()

            # Put form processing code here
            g.user.logger.info('Success - Alias Record Modified - Object ID: ' + util.safe_str(alias_record.get_id()))
            flash('Success - Alias Record Modified - Object ID: ' + util.safe_str(alias_record.get_id()), 'succeed')
            return redirect(url_for('update_alias_record_exampleupdate_alias_record_example_update_alias_record_example_page'))
        except Exception as e:
            flash(util.safe_str(e))
            # Log error and render workflow page
            g.user.logger.warning('%s' % util.safe_str(e), msg_type=g.user.logger.EXCEPTION)
            return render_template('update_alias_record_example_page.html',
                                   form=form,
                                   text=util.get_text(module_path(), config.language),
                                   options=g.user.get_options())
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template('update_alias_record_example_page.html',
                               form=form,
                               text=util.get_text(module_path(), config.language),
                               options=g.user.get_options())
