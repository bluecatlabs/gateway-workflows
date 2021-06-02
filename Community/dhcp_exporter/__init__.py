# Copyright 2021 BlueCat Networks (USA) Inc. and its affiliates
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
# By: BlueCat Networks
# Date: 2019-06-01
# Gateway Version: 21.5.1
# Description: DHCP Exporter init

type = 'ui'
sub_pages = [
    {
        'name'        : 'dhcp_exporter_page',
        'title'       : u'DHCP Exporter',
        'endpoint'    : 'dhcp_exporter/dhcp_exporter_endpoint',
        'description' : u'Export DHCP information as Excel/CSV Format specified network'
    },
]
