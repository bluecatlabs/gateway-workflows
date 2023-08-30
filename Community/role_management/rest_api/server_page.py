# Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates
import traceback

from flask import jsonify, make_response, g
from flask_restx import Resource

from bluecat import util
from bluecat.gateway.decorators import require_permission
from bluecat_libraries.http_client import ClientError

from ..common.exception import UserException
from .. import bp_rm
from .library.parsers.hint_parser import hint_parser
from ..rest_v2.common import get_id
from ..rest_v2.decorators import rest_v2_handler

server_ns = bp_rm.namespace(
    'Server  Resources',
    path='/configurations/<string:configuration_name>',
    description='Server operations'
)


@require_permission('rest_page')
@server_ns.route('/interfaces')
class InterfaceCollection(Resource):
    @rest_v2_handler
    @util.no_cache
    @server_ns.expect(hint_parser)
    def get(self, configuration_name):
        """Get all interfaces by hint"""
        if not g.user:
            return make_response("Authentication is required.", 401)
        try:
            args = hint_parser.parse_args()
            limit = args.get('limit', 10)
            hint = args.get('hint', '')
            api_v2 = g.user.v2
            configuration_response = api_v2.get_configuration_by_name(configuration_name)
            configuration_id = get_id(configuration_response)
            interfaces = api_v2.get_interfaces_by_hint(configuration_id, hint, limit)
            return make_response(jsonify(interfaces))

        except UserException as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 403)
        except ClientError as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 404)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


@require_permission('rest_page')
@server_ns.route('/servers')
class ServerCollection(Resource):
    @rest_v2_handler
    @util.no_cache
    @server_ns.expect(hint_parser)
    def get(self, configuration_name):
        """Get all servers by hint"""
        if not g.user:
            return make_response("Authentication is required.", 401)
        try:
            args = hint_parser.parse_args()
            limit = args.get('limit', 10)
            hint = args.get('hint', '')
            api_v2 = g.user.v2
            configuration_response = api_v2.get_configuration_by_name(configuration_name)
            configuration_id = get_id(configuration_response)
            servers = api_v2.get_servers_by_hint(configuration_id, hint, limit)
            return make_response(jsonify(servers))

        except UserException as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 403)
        except ClientError as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 404)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


@require_permission('rest_page')
@server_ns.route('/servers/<string:server>/interfaces')
class InterfaceByServerCollection(Resource):
    # @server_ns.expect(hint_parser)
    @rest_v2_handler
    @util.no_cache
    def get(self, configuration_name, server):
        """Get interfaces by server name"""
        if not g.user:
            return make_response("Authentication is required.", 401)
        try:
            api_v2 = g.user.v2
            configuration_response = api_v2.get_configuration_by_name(configuration_name)
            configuration_id = get_id(configuration_response)
            servers = api_v2.get_servers_by_hint(configuration_id, server)
            if servers.get('count') == 0:
                return make_response(jsonify(servers))
            server_id = get_id(servers)
            servers = api_v2.get_interfaces_by_server(server_id, fields='not(_links)')
            return make_response(jsonify(servers))
        except UserException as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 403)
        except ClientError as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 404)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)
