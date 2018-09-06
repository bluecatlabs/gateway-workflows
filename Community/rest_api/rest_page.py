# Copyright 2018 BlueCat Networks. All rights reserved.

from flask import request, g, abort, jsonify
from flask_restplus import Swagger, Resource, fields, reqparse

from bluecat import route, util
from main_app import app, api
import config.default_config as config
from . import ip_space_page
from . import dns_page
from . import configuration_page


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
                    for param_dict in api_paths[path][action]['parameters']:
                        resources[resource][action]['query_parameters'][param_dict['name']] = param_dict
                        if param_dict['name'] not in parsed_json['parameters']:
                            parsed_json['parameters'][param_dict['name']] = param_dict
        return parsed_json

