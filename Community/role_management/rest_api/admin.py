# Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates
import traceback

from flask import jsonify, g, make_response
from flask_restx import Resource

from bluecat import util
from bluecat.entity import Entity
from bluecat.gateway.decorators import require_permission

from .library.parsers.parent_parser import parent_parser
from .. import bp_rm
from ..rest_v2.constants import Collections
from bluecat_libraries.http_client import ClientError
from ..common.exception import (
    UserException
)
from ..rest_v2.decorators import rest_v2_handler

admin_ns = bp_rm.namespace(
    'Admin Resources',
    path='/',
    description='Admin operations',
)


@require_permission('rest_page')
@admin_ns.route('/parent/<string:objects_id>')
class ParentCollection(Resource):
    @rest_v2_handler
    @util.no_cache
    @admin_ns.expect(parent_parser)
    def get(self, objects_id):
        """Get parent by type"""
        if not g.user:
            return make_response("Authentication is required.", 401)
        try:
            args = parent_parser.parse_args()
            target_parent_type = args.get('collections', '')
            rest_v2 = g.user.v2
            result = {}
            for object_id in objects_id.split(','):
                try:
                    entity = rest_v2.get_entity_by_id(object_id)
                except IndexError:
                    g.user.logger.error("Object with id {} was not found".format(object_id))
                    result.update({object_id: {}})
                    continue

                valid_case = True
                exception_case = {Collections.CONFIGURATIONS: [],
                                  Collections.BLOCKS: [Entity.Server, Entity.Zone, Entity.View],
                                  Collections.SERVERS: [Entity.Zone, Entity.View],
                                  Collections.VIEWS: [Entity.View, Entity.Server],
                                  Collections.ZONES: [Entity.View, Entity.Server]}
                for value in exception_case[target_parent_type]:
                    if entity.get("type").endswith(value):
                        g.user.logger.error(
                            "Invalid collection {} for id {}".format(args.get('collections', ''), object_id))
                        valid_case = False

                if valid_case:
                    parent = entity
                    while not parent.get("type").lower().endswith(target_parent_type[:-1]) or parent == entity:
                        if parent.get("type") == Entity.Configuration or "up" not in parent.get("_links"):
                            g.user.logger.error(
                                "Invalid collection {} for id {}".format(args.get('collections', ''), object_id))
                            parent = {}
                            break
                        next_parent_id = parent.get("_links").get("up").get("href").split('/')[-1]
                        parent = rest_v2.get_entity_by_id(next_parent_id)
                    result.update({object_id: parent})
                else:
                    result.update({object_id: {}})

            return make_response(jsonify(result))

        except UserException as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 403)
        except ClientError as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 404)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)
