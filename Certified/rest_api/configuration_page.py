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

from flask import jsonify
from flask_restplus import Resource

import config.default_config as config
from bluecat import util
from main_app import api
from .library.models.configuration_models import configuration_model
from .library.models.entity_models import entity_return_model
from .library.parsers.deployment_parsers import deployment_option_post_parser
from .library.parsers.entity_parsers import entity_parser
from .option_and_role_utils import *

config_ns = api.namespace('configurations', description='Configuration operations')
config_doc = {'configuration': {'in': 'path', 'description': 'The name of the Configuration'}}

config_defaults = {'configuration': config.default_configuration}


@config_ns.route('/')
@config_ns.doc(params=config_doc)
class ConfigurationCollection(Resource):

    @util.rest_workflow_permission_required('rest_page')
    @config_ns.response(404, 'No matching Configuration(s) found')
    def get(self):
        """ Get all known Configuration(s). """
        configurations = g.user.get_api().get_configurations()
        result = [config_entity.to_json() for config_entity in configurations]
        return jsonify(result)

    @util.rest_workflow_permission_required('rest_page')
    @config_ns.expect(configuration_model)
    @config_ns.response(422, 'Error in POST data')
    @config_ns.response(409, 'Configuration already exists')
    def post(self):
        """ Create a new Configuration. """
        data = entity_parser.parse_args()
        configuration = g.user.get_api().create_configuration(data['name'])
        result = configuration.to_json()
        return result, 201


@config_ns.route('/<string:configuration>/')
@config_ns.doc(params=config_doc)
@config_ns.response(404, 'No matching Configuration(s) found')
class Configuration(Resource):

    @util.rest_workflow_permission_required('rest_page')
    def get(self, configuration):
        """ Get Configuration with specified name. """
        configuration = g.user.get_api().get_configuration(configuration)
        result = configuration.to_json()
        return jsonify(result)

    @util.rest_workflow_permission_required('rest_page')
    def delete(self, configuration):
        """ Delete Configuration with specified name. """
        configuration = g.user.get_api().get_configuration(configuration)
        configuration.delete()
        return '', 204


@config_ns.route('/<string:configuration>/option/<string:option_name>/server/<path:server_id>/deployment_options/')
@config_ns.response(200, 'Deployment Option found.', model=entity_return_model)
class DeploymentOptionCollection(Resource):

    @util.rest_workflow_permission_required('rest_page')
    def get(self, configuration, option_name, server_id):
        """
        Find a deployment option set on the configuration, by name and assigned server ID

        Server ID can be:

        1. 0 if the option is set to All Servers
        2. The entity ID of the assigned server or server group
        3. -1 if you are not sure which of the above to use
        """
        configuration = g.user.get_api().get_configuration(configuration)
        return get_option(configuration, option_name, int(server_id))

    @util.rest_workflow_permission_required('rest_page')
    def delete(self, configuration, option_name, server_id):
        """
        Delete a deployment option set on the configuration, by name and assigned server ID

        Server ID can be:

        1. 0 if the option is set to All Servers
        2. The entity ID of the assigned server or server group
        """
        configuration = g.user.get_api().get_configuration(configuration)
        if int(server_id) < 0:
            return 'Server ID must be 0 or higher for delete function', 400
        return del_option(configuration, option_name, int(server_id))


@config_ns.route('/<string:configuration>/deployment_options/')
class DeploymentOption(Resource):

    @util.rest_workflow_permission_required('rest_page')
    @config_ns.expect(deployment_option_post_model, validate=True)
    @config_ns.response(200, 'Deployment Option Assigned.', model=entity_return_model)
    def post(self, configuration):
        """
        Add a DNS or DHCP Deployment Option to the configuration
        """
        configuration = g.user.get_api().get_configuration(configuration)
        data = deployment_option_post_parser.parse_args()
        return add_option(configuration, data)
