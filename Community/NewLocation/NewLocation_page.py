# Copyright 2018 BlueCat Networks. All rights reserved.

# Various Flask framework items.
import os
import sys
import codecs

from flask import url_for, redirect, render_template, flash, g, request, jsonify

from bluecat import route, util
from bluecat.api_exception import PortalException
from bluecat.util import rest_exception_catcher, rest_workflow_permission_required
from bluecat.wtform_fields import SimpleAutocompleteField
import config.default_config as config
from main_app import app
from .NewLocation_form import GenericFormTemplate


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


SUCCESS = 'SUCCESS'
FAIL = 'FAIL'


def get_result_template():
    return {'status': FAIL, 'message': '', 'data': {}}


def empty_decorator(res):
    """
    Default 'do nothing' decorator applied to every result set.
    """
    return res


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/NewLocation/NewLocation_endpoint')
@util.workflow_permission_required('NewLocation_page')
@util.exception_catcher
def NewLocation_NewLocation_page():
    form = GenericFormTemplate()
    return render_template(
        'NewLocation_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )

@route(app, '/NewLocation/form', methods=['POST'])
@util.workflow_permission_required('NewLocation_page')
@util.exception_catcher
def NewLocation_NewLocation_page_form():
    form = GenericFormTemplate()
    if form.validate_on_submit():

        loc_code_start = form.parent_location.data.rfind('(') + 1
        loc_code_end = form.parent_location.data.rfind(')', loc_code_start)
        loc_code = form.parent_location.data[loc_code_start:loc_code_end]
        loc_name_end = loc_code_start - 2
        loc_name = form.parent_location.data[:loc_name_end]

        foundlocations = g.user.get_api().get_by_object_types(loc_name, 'Location')
        location_id = 0
        location_sub = ''
        location_country = ''
        for location in foundlocations:
            if location.get_name() == loc_name and location.get_property('code') == loc_code:
                location_id = location.get_id()
                location_sub = location.get_property('subDivision')
                location_country = location.get_property('country')

        new_location_code = loc_code + ' ' + form.new_location_code.data

        new_location = {'name': form.new_location_name.data,
                        'type': 'Location',
                        'properties': 'code=%s|country=%s|localizedName=%s|subDivision=%s' %
                                      (new_location_code, location_country, form.new_location_name.data, location_sub)}


        new_location_id = g.user.get_api()._api_client.service.addEntity(location_id, new_location)
        g.user.logger.info('SUCCESS')
        flash('Created the new location! ID: %s, Name: %s, Code: %s' % (new_location_id, form.new_location_name.data, new_location_code), 'succeed')
        return redirect(url_for('NewLocationNewLocation_NewLocation_page'))
    else:
        g.user.logger.info('Form data was not valid.')
        return render_template(
            'NewLocation_page.html',
            form=form,
            text=util.get_text(module_path(), config.language),
            options=g.user.get_options(),
        )
