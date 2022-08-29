# Copyright 2022 BlueCat Networks (USA) Inc. and its affiliates
# -*- coding: utf-8 -*-
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
# By: BlueCat Networks Inc.
# Date: 2022-05-01
# Gateway Version: 21.11.2
# Description: Health Telemetries Endpoint health_telemetries_page.py

from flask import request, g, abort, jsonify

from bluecat import route, util
from main_app import app

from .telemetry_buffer import TelemetryBuffer


@route(app, '/api/v1/health_telemetries/dns_activities', methods=['GET', 'PUT', 'POST'])
@util.rest_exception_catcher
def health_telemetries_dns_activities():
    t_buffer = TelemetryBuffer.get_instance()
    for data in request.get_json():
        t_buffer.push('activity', data['key'], data)
    return jsonify(success=True)

@route(app, '/api/v1/health_telemetries/dns_statistics', methods=['GET', 'PUT', 'POST'])
@util.rest_exception_catcher
def health_telemetries_dns_statistics():
    t_buffer = TelemetryBuffer.get_instance()
    for data in request.get_json():
        t_buffer.push('dns', data['key'], data)
    return jsonify(success=True)

@route(app, '/api/v1/health_telemetries/dhcp_statistics', methods=['GET', 'PUT', 'POST'])
@util.rest_exception_catcher
def health_telemetries_dhcp_statistics():
    t_buffer = TelemetryBuffer.get_instance()
    for data in request.get_json():
        t_buffer.push('dhcp', data['key'], data)
    return jsonify(success=True)
