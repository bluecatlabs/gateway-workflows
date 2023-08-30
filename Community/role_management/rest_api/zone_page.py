# Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates
import traceback
from flask import jsonify, make_response, g
from flask_restx import Resource
from bluecat import util
from bluecat.gateway.decorators import require_permission
from bluecat_libraries.http_client import ClientError

from .library.parsers.hint_parser import zone_by_hint_parser
from .. import bp_rm

from ..common.exception import UserException
from ..rest_v2.common import get_id
from ..rest_v2.decorators import rest_v2_handler

zone_ns = bp_rm.namespace(
    'Zone Resources',
    path='/configurations/<string:configuration_name>/zones',
    description='Zone operations'
)


@require_permission('rest_page')
@zone_ns.route('')
class ZoneCollection(Resource):
    @rest_v2_handler
    @util.no_cache
    @zone_ns.expect(zone_by_hint_parser)
    def get(self, configuration_name):
        """Get all zones by hint"""
        if not g.user:
            return make_response("Authentication is required.", 401)
        try:
            args = zone_by_hint_parser.parse_args()
            limit = args.get('limit', 10)
            hint = args.get('hint', '')
            view_name = args.get('view_name', '')
            api_v2 = g.user.v2
            configuration_response = api_v2.get_configuration_by_name(configuration_name)
            configuration_id = get_id(configuration_response)
            ancestor_id = configuration_id
            if view_name:
                view_response = api_v2.get_view_in_configuration_by_name(configuration_id, view_name)
                ancestor_id = get_id(view_response)
            zones = api_v2.get_zones_by_hint(ancestor_id, hint, limit)
            return make_response(jsonify(zones))
        except UserException as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 403)
        except ClientError as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 404)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)
