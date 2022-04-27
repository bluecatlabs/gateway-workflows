# Copyright 2020-2022 BlueCat Networks (USA) Inc. and its affiliates
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
# Date: 2022-04-28
# Gateway Version: 22.4.1
# Description: Example Gateway workflow

"""This file is responsible for populating the out put table in selective deploy"""
from itertools import chain
from flask import g
from flask import jsonify
from flask import request

from main_app import app
from bluecat import route
from bluecat.util import rest_exception_catcher
from bluecat.util import rest_workflow_permission_required
from bluecat.server_endpoints import empty_decorator
from bluecat.server_endpoints import get_result_template


def raw_table_data(*args, **kwargs):
    # pylint: disable=unused-argument
    """Returns table formatted data for display in the TableField component"""
    return {
        "columns": [
            {"title": "Id"},
            {"title": "Name"},
            {"title": "Type"},
            {"title": "Select"},
        ],
        "data": [],
        "columnDefs": [{"width": "10%", "targets": [3]}],
    }


def raw_entities_to_table_data(entities, in_search):
    """
    Convert raw entities from a direct API call into table data of the form:
    data = {
        "columns": [
            {"title": "Heading1"},
            {"title": "Heading2"}
        ],
        "data": [
            ["dat1", "dat2"],
            ["dat3", "dat4"]
        }
    }
    Where the length of each list in data['data'] must equal to the number of columns

    :param entities: Response object containing entities from a direct API call
    :param in_search: a boolean variable the the stat of the table is in search or not
    :param return: Dictionary of data parsable by the UI Table Component
    """
    data = {"columns": [], "data": []}

    if in_search:
        data["columns"] = [
            {"title": "Id"},
            {"title": "Name"},
            {"title": "Type"},
            {"title": "Select"},
        ]
    else:
        data["columns"] = [
            {"title": "Id"},
            {"title": "Name"},
            {"title": "Type"},
            {"title": "Status"},
        ]

    # Iterate through each entity
    for entries in entities:
        if in_search:
            data["data"].append(
                [
                    entries.get_id(),
                    entries.name,
                    entries.get_type(),
                    '<input type="checkbox" name=%s>' % entries.get_id(),
                ]
            )
        else:
            new_entries = g.user.get_api().get_entity_by_id(entries)
            data["data"].append(
                [new_entries.get_id(), new_entries.name, new_entries.get_type(), entities[entries]]
            )

    return data


def find_objects_by_type_endpoint(workflow_name, element_id, permissions, result_decorator=None):
    """Endpoint for retrieving the selected objects"""
    endpoint = "find_objects_by_type"
    function_endpoint = "%sfind_objects_by_type" % workflow_name
    view_function = app.view_functions.get(function_endpoint)
    if view_function is not None:
        return endpoint
    if not result_decorator:
        result_decorator = empty_decorator

    g.user.logger.info("Creating endpoint %s", endpoint)
    g.user.logger.info("element id %s", element_id)

    @route(app, "/%s/%s" % (workflow_name, endpoint), methods=["POST"])
    @rest_workflow_permission_required(permissions)
    @rest_exception_catcher
    def find_objects_by_type():
        # pylint: disable=unused-variable
        """Retrieve a list of properties for the table"""

        try:
            configuration = g.user.get_api().get_entity_by_id(request.form["configuration"])
            view = configuration.get_view(request.form["view"])
            zone_string = request.form["zone"].split(".")

            zone = view
            for i in range(len(zone_string) - 1, -1, -1):
                zone = zone.get_zone(zone_string[i])

            entities = chain(
                zone.get_children_of_type("HostRecord"),
                zone.get_children_of_type("AliasRecord"),
                zone.get_children_of_type("TXTRecord"),
                zone.get_children_of_type("HINFORecord"),
                zone.get_children_of_type("SRVRecord"),
                zone.get_children_of_type("MXRecord"),
                zone.get_children_of_type("NAPTRRecord"),
            )

            data = raw_entities_to_table_data(entities, True)

            result = get_result_template()
            data["columnDefs"] = [{"width": "10%", "targets": [3], "render": ""}]
            if not data["data"]:
                result["message"] = "No DNS Records Found"
            result["status"] = "SUCCESS"
            result["data"] = {"table_field": data}
            return jsonify(result_decorator(result))

        except Exception as error:
            result = get_result_template()
            result["status"] = "FAIL"
            result["message"] = str(error)

            return jsonify(result_decorator(result))

    return endpoint
