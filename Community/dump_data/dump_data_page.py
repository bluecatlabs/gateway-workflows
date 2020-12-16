# Copyright 2020 BlueCat Networks. All rights reserved.
import os
import sys
import io
import csv

from flask import url_for, redirect, render_template, flash, g, make_response, jsonify

from bluecat import route, util
from bluecat.util import rest_exception_catcher, rest_workflow_permission_required
from bluecat.entity import Entity
from bluecat.api_exception import APIException, PortalException, BAMException
import config.default_config as config
from main_app import app
from .dump_data_form import GenericFormTemplate


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


# The workflow name must be the first part of any endpoints defined in this file.
# If you break this rule, you will trip up on other people's endpoint names and
# chaos will ensue.
@route(app, '/dump_data/dump_data_endpoint')
@util.workflow_permission_required('dump_data_page')
@util.exception_catcher
@util.ui_secure_endpoint
def dump_data_dump_data_page():
    form = GenericFormTemplate()
    return render_template(
        'dump_data_page.html',
        form=form,
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )


def get_records_info(zone, entity_types):
    records = []
    for entity_type in entity_types:
        for record in zone.get_children_of_type(entity_type):
            if record.get_type() == Entity.GenericRecord:
                if record.get_property('type') == 'A':
                    records.append({'record_id': record.get_id(),
                                   'record_type': '{} - {}'.format(record.get_type(), 'A'),
                                   'record_name': record.get_full_name(),
                                   'record_link':  record.get_property('rdata'),
                                   'properties': util.map_to_properties(record.get_properties())})
            else:
                records.append({'record_id': record.get_id(),
                               'record_type': record.get_type(),
                               'record_name': record.get_full_name(),
                               'record_link':  '|'.join(record.get_addresses()) if record.get_type() == Entity.HostRecord else record.get_linked_record_name(),
                               'properties': util.map_to_properties(record.get_properties())})

    return records


def get_records(zone):
    found_records = []

    found_records.extend(get_records_info(zone, [Entity.HostRecord, Entity.AliasRecord, Entity.GenericRecord]))

    for sub_zone in zone.get_zones():
        found_records.extend(get_records(sub_zone))

    return found_records


def generate_csv_string(data, column_headers):
    string_output = io.StringIO()
    csv_writer = csv.writer(string_output)

    csv_writer.writerow(column_headers)

    column_translation = []
    for column in column_headers:
        column_translation.append(column.lower().replace(' ', '_'))

    for row in data:
        row_data = []
        for column in column_translation:
            row_data.append(row[column])
        csv_writer.writerow(row_data)

    return string_output.getvalue()


def retrieve_records():
    records = []
    configuration = g.user.get_api().get_configuration(config.default_configuration)
    views = configuration.get_views()

    for view in views:
        for zone in view.get_zones():
            records.extend(get_records(zone))

    return records


@route(app, '/dump_data/form', methods=['POST'])
@util.workflow_permission_required('dump_data_page')
@util.exception_catcher
@util.ui_secure_endpoint
def dump_data_dump_data_page_form():
    column_headers = ['Record ID', 'Record Type', 'Record Name', 'Record Link', 'Properties']

    try:
        records = retrieve_records()

        csv_data = generate_csv_string(records, column_headers)

        output_response = make_response(csv_data)
        output_response.headers['Content-Disposition'] = 'attachment; filename=records.csv'
        output_response.headers['Content-type'] = 'text/csv'

        return output_response
    except (APIException, BAMException, PortalException) as e:
        flash('Encountered an error while processing the data: {}'.format(util.safe_str(e)))
        return redirect(url_for('dump_datadump_data_dump_data_page'))


@route(app, '/dump_data/get_records', methods=['GET'])
@rest_workflow_permission_required('dump_data_page')
@rest_exception_catcher
def get_records_endpoint():
    try:
        records = retrieve_records()

        returned_data = {'configuration': config.default_configuration,
                         'records': records}

        return jsonify(returned_data)
    except (PortalException, BAMException, APIException) as e:
        error_return = {'failed': True,
                        'message': 'Encountered an exception while retrieving host records: %s' % util.safe_str(e)}
        return jsonify(error_return)
