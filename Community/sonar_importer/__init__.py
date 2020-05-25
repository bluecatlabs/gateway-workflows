# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates
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
# By: Akira Goto (agoto@bluecatnetworks.com)
# Date: 2019-10-30
# Gateway Version: 19.8.1
# Description: Fixpoint Kompira Cloud Sonar Importer __init__.py

type = 'ui'
sub_pages = [
    {
        'name'        : 'sonar_importer_page',
        'title'       : u'Sonar Importer',
        'endpoint'    : 'sonar_importer/sonar_importer_endpoint',
        'description' : u'Import IPAM data from Kompira Cloud Sonar'
    },
]
