# Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates
import traceback

from flask import jsonify, g, make_response
from flask_restx import Resource

from bluecat import util
from bluecat.gateway.decorators import require_permission

from ..common.exception import UserException


from .. import bp_rm
from ..rest_v2.decorators import rest_v2_handler

configuration_ns = bp_rm.namespace(
    'Configuration Resources',
    path='/',
    description='configuration operations',
    )


@require_permission('rest_page')
@configuration_ns.route('/configurations')
class Configurations(Resource):
    @rest_v2_handler
    @util.no_cache
    def get(self):
        """ Get all configuration(s) """
        try:
            bam_api = g.user.v2
            result = []
            configurations = bam_api.get_configurations()
            for config in configurations.get("data"):
                result.append(
                    {
                        "id": config.get("id"),
                        "name": config.get("name"),
                        "type": config.get("type")
                    }
                )
            return make_response(jsonify(result))
        except UserException as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 403)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


@require_permission('rest_page')
@configuration_ns.route('/configuration/<configuration_name>')
class Configuration(Resource):
    @rest_v2_handler
    @util.no_cache
    def get(self, configuration_name):
        """ Get configuration by name """
        try:
            bam_api = g.user.v2
            config = bam_api.get_configuration_by_name(configuration_name)
            config = config.get("data")[0]
            result = {
                "id": config.get("id"),
                "name": config.get("name"),
                "type": config.get("type")
            }
            return make_response(jsonify(result))
        except UserException as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 403)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


