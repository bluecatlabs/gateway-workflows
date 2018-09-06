# Copyright 2018 BlueCat Networks. All rights reserved.

from flask import g, jsonify
from flask_restplus import fields, Resource, reqparse

from bluecat import util
import config.default_config as config
from main_app import api


config_ns = api.namespace('configurations', description='Configuration operations')
config_doc = {'configuration': {'in': 'path', 'description': 'The name of the Configuration'}}

entity_parser = reqparse.RequestParser()
entity_parser.add_argument('name', location="json", help='The name of the entity.')
entity_parser.add_argument(
    'properties',
    location="json",
    help='The properties of the entity in the following format:key=value|key=value|',
)

entity_model = api.model(
    'Entity Parameters',
    {
        'name': fields.String(description='The name of the entity.'),
        'properties':  fields.String(
            description='The properties of the entity in the following format:key=value|key=value|'
        ),
    },
)

entity_return_model = api.model(
    'Entity Object',
    {
        'id': fields.Integer(description='ID of the entity.'),
        'name': fields.String(description='The name of the entity.'),
        'type': fields.String(description='The type of the entity.'),
        'properties':  fields.String(
            description='The properties of the entity in the following format:key=value|key=value|'
        ),
    },
)


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
    @config_ns.expect(entity_parser)
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

