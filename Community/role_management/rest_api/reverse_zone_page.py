# Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates
import traceback

from flask import jsonify, make_response, g
from flask_restx import Resource
from bluecat import util
from bluecat.gateway.decorators import require_permission
from bluecat_libraries.http_client import ClientError

from .library.parsers.hint_parser import hint_parser
from .. import bp_rm
from ..common.exception import UserException
from ..rest_v2.common import get_id
from ..common.common import get_range_hint_from_reverse_zone
from ..rest_v2.decorators import rest_v2_handler

reverse_zone_range_ns = bp_rm.namespace(
    'Reverse Zone Resources',
    path='/configurations/<string:configuration_name>/reverse_zones',
    description='Reverse Zones operations'
)


@require_permission('rest_page')
@reverse_zone_range_ns.route('')
class ReverseZoneCollection(Resource):
    @rest_v2_handler
    @util.no_cache
    @reverse_zone_range_ns.expect(hint_parser)
    def get(self, configuration_name: str):
        """Get all reverse zones by hint"""
        if not g.user:
            return make_response("Authentication is required.", 401)
        try:
            args = hint_parser.parse_args()
            limit = args.get('limit', 10)
            hint = args.get('hint', '')
            hint_dictionary = get_range_hint_from_reverse_zone(hint)
            ipv4_hint = hint_dictionary.get('ipv4_hint', '')
            ipv6_hint = hint_dictionary.get('ipv6_hint', '')
            raw_hint = hint_dictionary.get('raw_hint', '')
            # case hint included but not having any digit character
            if len(hint.strip()) > 0 and not ipv4_hint and not ipv6_hint:
                return make_response(jsonify({
                    'count': 0,
                    'data': [],
                    'totalCount': 0
                }))
            api_v2 = g.user.v2
            configuration_response = api_v2.get_configuration_by_name(configuration_name)
            configuration_id = get_id(configuration_response)
            reverse_zone_ranges = api_v2.get_networks_and_blocks_by_ipv4_and_ipv6_hint(configuration_id,
                                                                                       ipv4_hint=ipv4_hint,
                                                                                       ipv6_hint=ipv6_hint,
                                                                                       raw_hint=raw_hint,
                                                                                       limit=limit)
            return make_response(jsonify(reverse_zone_ranges))
        except UserException as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 403)
        except ClientError as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 404)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)
