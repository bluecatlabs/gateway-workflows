# Copyright 2020 BlueCat Networks. All rights reserved.
import os
import sys
import csv
from time import strftime, gmtime

from flask import render_template, g, send_from_directory, flash, redirect, url_for, after_this_request

from main_app import app
from bluecat import route, util
import config.default_config as config
from bluecat.api_exception import PortalException
from .acl_inventory_form import GenericFormTemplate
from .acl_inventory_util import safe_open, generate_filename


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/acl_inventory/acl_inventory_endpoint')
@util.workflow_permission_required('acl_inventory_page')
@util.exception_catcher
def acl_inventory_acl_inventory_page():
    # Define variables
    form = GenericFormTemplate()
    return render_template(
        'acl_inventory_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )


@route(app, '/acl_inventory/form', methods=['POST'])
@util.workflow_permission_required('acl_inventory_page')
@util.exception_catcher
def acl_inventory_acl_inventory_page_form():
    # Define variables
    form = GenericFormTemplate()
    # Create a secure filename to store acl results
    acl_report_filename = generate_filename('acl_inventory.csv')

    # Retrieve acl entity
    try:
        acl = g.user.get_api().get_entity_by_id(form.acls_list.data)
    except PortalException as e:
        g.user.logger.error('%s' % e, msg_type=g.user.logger.EXCEPTION)
        flash('Unable to retrieve the selected ACL - Please try again')
        return redirect(url_for('acl_inventoryacl_inventory_acl_inventory_page'))

    # Retrieve IP addresses associated with ACL
    try:
        value_list = acl.get_property('aclValues').split(',')
    except ValueError as e:
        g.user.logger.error('%s' % e, msg_type=g.user.logger.EXCEPTION)
        flash('An unexpected error occurred')
        return redirect(url_for('acl_inventoryacl_inventory_acl_inventory_page'))

    with safe_open('bluecat_portal/workflows/acl_inventory/temp_directory/%s' % acl_report_filename) as output_report:
        # Create csv writer object to write to output file
        csv_writer = csv.writer(output_report)
        csv_writer.writerow(['ACL Report for %s generated on %s'
                             % (acl.get_name(), strftime("%H:%M %d-%m-%Y", gmtime()))])

        # For each IP retrieve associated host records
        for value in value_list:
            csv_writer.writerow([value])

    @after_this_request
    def delete_file(response):
        os.remove('bluecat_portal/workflows/acl_inventory/temp_directory/%s' % acl_report_filename)
        return response

    return send_from_directory(directory='bluecat_portal/workflows/acl_inventory/temp_directory/',
                               filename=acl_report_filename,
                               as_attachment=True)
