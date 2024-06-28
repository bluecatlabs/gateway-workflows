# Copyright 2024 BlueCat Networks (USA) Inc. and its affiliates
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
# Date: 2024-06-26
# Gateway Version: 24.3.0
# Description: Gateway workflow to demonstrate use of REST API v2 client.

"""
Navigate zones page
"""
from bluecat import route
from bluecat.address_manager import BAMAPI
from bluecat.gateway.decorators import api_exc_handler, page_exc_handler, require_permission
from bluecat.util import no_cache
from bluecat_libraries.address_manager.api import Client as V1Client
from bluecat_libraries.address_manager.apiv2 import Client as V2Client
from bluecat_libraries.address_manager.constants import ObjectType
from dataclasses import dataclass
from flask import g, jsonify, render_template, request
from main_app import app


@dataclass(init=True, frozen=True)
class IdNamePair:
    """Class for holding ID and name"""

    id: int
    name: str


def items_to_pairs(data) -> list[IdNamePair]:
    """
    Convert the data into IdNamePair class object

    :return: A list of IdNamePair Object
    """
    return [IdNamePair(id=o["id"], name=o["name"]) for o in data]


# region BAM actions


def _get_configurations_v1(client: V1Client) -> list[IdNamePair]:
    """
    Get configurations using REST v1 client

    :return: A list of IdNamePair Object
    """
    data = client.get_entities(0, ObjectType.CONFIGURATION, 0, 9999)  # NOTE: Hard-coded count.
    return items_to_pairs(data)


def _get_configurations_v2(client: V2Client) -> list[IdNamePair]:
    """
    Get configurations using REST v2 client

    :return: A list of IdNamePair Object
    """
    rdata = client.http_get(
        "/configurations", params={"fields": "id,name", "orderBy": "desc(name)", "limit": "9999"}
    )
    data = rdata["data"]
    return items_to_pairs(data)


def get_configurations(bam_api: BAMAPI) -> list[IdNamePair]:
    """
    Get configurations based on which version of API is configured on Gateway

    :return: A list of IdNamePair Object
    """
    return _get_configurations_v2(bam_api.v2) if bam_api.v2 else _get_configurations_v1(bam_api.v1)


def _get_views_v1(client: V1Client, parent_id: int) -> list[IdNamePair]:
    """
    Get views using REST v1 client

    :return: A list of IdNamePair Object
    """
    data = client.get_entities(parent_id, ObjectType.VIEW, 0, 9999)  # NOTE: Hard-coded count.
    return items_to_pairs(data)


def _get_views_v2(client: V2Client, parent_id: int) -> list[IdNamePair]:
    """
    Get views using REST v2 client

    :return: A list of IdNamePair Object
    """
    rdata = client.http_get(
        f"/configurations/{parent_id}/views",
        params={"fields": "id,name", "orderBy": "desc(name)", "limit": "9999"},
    )
    data = rdata["data"]
    return items_to_pairs(data)


def get_views_in(bam_api: BAMAPI, parent_id: int) -> list[IdNamePair]:
    """
    Get views based on which version of API is configured on Gateway

    :return: A list of IdNamePair Object
    """
    return (
        _get_views_v2(bam_api.v2, parent_id) if bam_api.v2 else _get_views_v1(bam_api.v1, parent_id)
    )


def _get_zones_v1(client: V1Client, parent_id: int) -> list[IdNamePair]:
    """
    Get zones using REST v2 client

    :return: A list of IdNamePair Object
    """
    data = client.get_entities(parent_id, ObjectType.ZONE, 0, 9999)  # NOTE: Hard-coded count.
    return items_to_pairs(data)


def _get_zones_v2(client: V2Client, parent_id: int) -> list[IdNamePair]:
    """
    Get zones using REST v2 client

    :return: A list of IdNamePair Object
    """
    rdata = client.http_get(
        f"/views/{parent_id}/zones",
        params={"fields": "id,name", "orderBy": "desc(name)", "limit": "9999"},
    )
    data = rdata["data"]
    return items_to_pairs(data)


def get_zones_in(bam_api: BAMAPI, parent_id: int) -> list[IdNamePair]:
    """
    Get zones based on which version of API is configured on Gateway

    :return: A list of IdNamePair Object
    """
    return (
        _get_zones_v2(bam_api.v2, parent_id) if bam_api.v2 else _get_zones_v1(bam_api.v1, parent_id)
    )


# endregion BAM actions
# region Page


@route(app, "/nav_zones/", methods=["GET"])
@no_cache
@page_exc_handler
@require_permission("nav_zones_page")
def page():
    """
    Renders the page the user would see when selecting the workflow

    :return:
    """
    return render_template("nav_zones.html")


# endregion Page
# region Data API


@route(app, "/nav_zones/api/v1/configurations/", methods=["GET"])
@no_cache
@api_exc_handler
@require_permission("nav_zones_page")
def configurations():
    """
    Retrieves the configurations available in Address Manager

    :return:
    """
    data = get_configurations(g.user.bam_api)
    return jsonify(data)


@route(app, "/nav_zones/api/v1/views/", methods=["GET"])
@no_cache
@api_exc_handler
@require_permission("nav_zones_page")
def views():
    """
    Retrieves the views available in Address Manager

    :return:
    """
    parent_id = request.args["parent_id"]
    data = get_views_in(g.user.bam_api, parent_id)
    return jsonify(data)


@route(app, "/nav_zones/api/v1/zones/", methods=["GET"])
@no_cache
@api_exc_handler
@require_permission("nav_zones_page")
def zones():
    """
    Retrieves the zones available in Address Manager

    :return:
    """
    parent_id = request.args["parent_id"]
    data = get_zones_in(g.user.bam_api, parent_id)
    return jsonify(data)


# endregion Data API
