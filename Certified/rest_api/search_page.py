# Copyright 2020 BlueCat Networks (USA) Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By: Xiao Dong, Anshul Sharma, Chris Storz (cstorz@bluecatnetworks.com) Date: 06-09-2018
# Gateway Version: 19.8.1
# Description: This workflow will provide access to a REST-based API for BlueCat Gateway.
#              Once imported and permissioned, documentation for the various available endpoints
#              can be viewed by navigating to /api/v1/.

from flask import g
from flask_restplus import Resource

from bluecat import util
from main_app import api
from .library.models.entity_models import entity_return_model

search_ns = api.namespace('search', path='/', description='Search for any object of the specified type')


@search_ns.route(
    '/search_pattern/<string:search_pattern>/object_type/<string:object_type>/search/<path:search_filters>/'
)
@search_ns.response(200, 'Objects found', model=entity_return_model)
class ObjectSearch(Resource):

    @util.rest_workflow_permission_required('rest_page')
    def get(self, search_pattern, object_type, search_filters):
        """
        Search for entities of the specified object type. Only the first 1000 possible results will be returned.

        filters can be in the format of property=value pairs:

        1. property=value
        2. property1=value,property2=value
        3. property1=value/search/property2=value

        pattern can be a name, ip address, or cidr address. The value can be full or partial and accepts basic regex.
        """
        if search_filters.lower() != 'none':
            filters = search_filters.split('/search')
            properties_to_check = {}
            num_properties_to_check = len(filters)
            for item in filters:
                values = item.strip().lower().split('=')
                properties_to_check[values[0]] = '='.join([x for x in values[1::]])
        else:
            num_properties_to_check = 0
            properties_to_check = {}
        if search_pattern.lower() in ['none', '*']:
            return 'You must specify a search pattern to use', 404

        results_to_return = []
        results = g.user.get_api().search_by_object_types(search_pattern, object_type)
        for result in results:
            if len(results_to_return) == 1000:
                break
            prop_check = result.get_properties()
            if num_properties_to_check == 0:
                results_to_return.append(result.to_json())
                continue
            n = 0
            for k, v in prop_check.items():
                l = k.lower()
                r = v.lower()
                if l in properties_to_check.keys():
                    if r == properties_to_check[l] or properties_to_check[l] in r:
                        n += 1
            if n == num_properties_to_check:
                results_to_return.append(result.to_json())

        return results_to_return, 200
