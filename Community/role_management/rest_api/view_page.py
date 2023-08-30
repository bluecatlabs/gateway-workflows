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
from ..rest_v2.decorators import rest_v2_handler

view_ns = bp_rm.namespace(
    'View Resources',
    path='/configurations/<string:configuration_name>/views',
    description='View operations'
)


@require_permission('rest_page')
@view_ns.route('')
class ViewCollection(Resource):
    @rest_v2_handler
    @util.no_cache
    @view_ns.expect(hint_parser)
    def get(self, configuration_name: str):
        """Get all views by hint"""
        if not g.user:
            return make_response("Authentication is required.", 401)
        try:
            args = hint_parser.parse_args()
            limit = args.get('limit', 10)
            hint = args.get('hint', '')
            api_v2 = g.user.v2
            configuration_response = api_v2.get_configuration_by_name(configuration_name)
            configuration_id = get_id(configuration_response)
            views = api_v2.get_views_by_hint(configuration_id, hint, limit)
            return make_response(jsonify(views))
        except UserException as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 403)
        except ClientError as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 404)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)
