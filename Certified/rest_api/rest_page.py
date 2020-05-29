# Copyright 2018 BlueCat Networks (USA) Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By: Xiao Dong (xdong@bluecatnetworks.com)
#     Anshul Sharma (asharma@bluecatnetworks.com)
# Date: 06-09-2018
# Gateway Version: 18.9.1
# Description: This workflow will provide access to a REST based API for Gateway.
#              Once imported, documentation for the various end points available can
#              be viewed by navigating to /api/v1/.

from flask import g, jsonify
from flask_restplus import Resource

from bluecat import util
from main_app import api
from . import ip_space_page
from . import dns_page
from . import configuration_page
from . import search_page


@api.route('/ddi/')
class ddi(Resource):

    @util.rest_workflow_permission_required('rest_page')
    def get(self):
        """ Get JSON of all available configurations and views in BAM. """
        configurations = g.user.get_api().get_configurations()
        data = {}
        for configuration in configurations:
            data[configuration.name] = {"id": configuration.get_id(), "views": []}
            views = configuration.get_views()
            for view in views:
                data[configuration.name]["views"].append(view.name)
        return jsonify(data)


@api.route('/gateway_api_json/')
class APIs(Resource):

    def get(self):
        """ Get JSON describing all the available Gateway REST API endpoints. """
        return self.parse_json(api.__schema__)

    def parse_json(self, api_json):
        parsed_json = {'resources': {}, 'parameters': {}}
        resources = parsed_json['resources']
        api_paths = api_json['paths']
        for path in api_paths:
            path_parts = path.strip('/').split('/')
            if path_parts[-1].startswith('{') and path_parts[-1].endswith('}'):
                resource = path_parts[-2]
            else:
                resource = path_parts[-1]
            if resource not in resources:
                resources[resource] = {}

            for action in api_paths[path]:
                if action not in resources[resource]:
                    resources[resource][action] = {'paths': [path], 'path_parameters': {}, 'query_parameters': {}}
                else:
                    resources[resource][action]['paths'].append(path)
                resources[resource][action]['path_parameters'][path] = {}
                if 'parameters' in api_paths[path]:
                    for param_dict in api_paths[path]['parameters']:
                        if 'required' in param_dict and param_dict['required'] == True:
                            resources[resource][action]['path_parameters'][path][param_dict['name']] = param_dict
                        if param_dict['name'] not in parsed_json['parameters']:
                            parsed_json['parameters'][param_dict['name']] = param_dict
                if 'parameters' in api_paths[path][action]:
                    if action.lower() == 'patch':
                        resource_nm = resource + '_patch'
                    else:
                        resource_nm = resource

                    if (action.lower() == 'post' or action.lower() == 'patch') and resource_nm in api_json[
                        'definitions']:
                        required_list = []
                        if 'required' in api_json['definitions'][resource_nm]:
                            required_list = api_json['definitions'][resource_nm]['required']
                        for name, param_dict in api_json['definitions'][resource_nm]['properties'].items():
                            param_dict['name'] = name
                            param_dict['required'] = False
                            if name in required_list:
                                param_dict['required'] = True
                            resources[resource][action]['query_parameters'][param_dict['name']] = param_dict
                            if param_dict['name'] not in parsed_json['parameters']:
                                parsed_json['parameters'][param_dict['name']] = param_dict
                    for param_dict in api_paths[path][action]['parameters']:
                        resources[resource][action]['query_parameters'][param_dict['name']] = param_dict
                        if param_dict['name'] not in parsed_json['parameters']:
                            parsed_json['parameters'][param_dict['name']] = param_dict
        return parsed_json
