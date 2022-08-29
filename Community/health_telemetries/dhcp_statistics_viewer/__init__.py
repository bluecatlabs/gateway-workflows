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
# Description: Health Telemetry DHCP Statistics Viewer __init__.py
# -*- coding: utf-8 -*-

type = 'ui'
sub_pages = [
    {
        'name'        : 'dhcp_statistics_viewer_page',
        'title'       : u'DHCP Statistics Viewer',
        'endpoint'    : 'dhcp_statistics_viewer/dhcp_statistics_viewer_endpoint',
        'description' : u'DHCP Statistics Viewer'
    },
]
