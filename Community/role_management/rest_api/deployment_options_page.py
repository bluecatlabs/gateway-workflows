# Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates
import traceback

from flask import jsonify, g, make_response
from flask_restx import Resource

from bluecat import util
from bluecat.entity import Entity
from bluecat.gateway.decorators import require_permission

from bluecat_libraries.address_manager.apiv2 import BAMV2ErrorResponse
from bluecat_libraries.http_client import UnexpectedResponse

from .library.models import deployment_option_models

from .library.parsers import deployment_option_parsers
from .. import bp_rm
from ..rest_v2 import common
from ..rest_v2.constants import Collections, ZoneTypeCls, EntityV2
from ..common.exception import (
    UserException,
    BAMAuthException,
    InvalidParam,
)
from ..rest_v2.decorators import rest_v2_handler

deployment_option_ns = bp_rm.namespace(
    'Deployment Option Resources',
    path='/',
    description='Deployment Option operations',
)


@util.exception_catcher
@require_permission('rest_page')
@deployment_option_ns.route('/configurations/<string:configuration>/deployment_options')
class DeploymentOptionCollection(Resource):
    @rest_v2_handler
    @util.no_cache
    @deployment_option_ns.expect(deployment_option_parsers.deployment_option_parser)
    def get(self, configuration):
        """ Retrieve a collection of all deployment options configured for a resource.
        """
        try:
            data = deployment_option_parsers.deployment_option_parser.parse_args()
            collection = data.get('collection')
            collection_name = data.get('collection_name')
            if not collection_name:
                raise InvalidParam('Missing Collection Name.')
            rest_v2 = g.user.v2
            configuration_js = rest_v2.get_configuration_by_name(configuration).get('data')[0]
            collection_type = Collections.get_entity_type(collection)
            ancestor = 'ancestor.id:{}'.format(configuration_js.get('id'))

            collection_rs = {
                "count": 0
            }
            if collection in ZoneTypeCls.FORWARDER_ZONE:
                view = data.get('view')
                if collection == Collections.ZONES and not view:
                    raise InvalidParam('Missing view.')
                view_js = rest_v2.get_v2(
                    "ancestor.id:{} and name:'{}' and type:'{}'".format(configuration_js.get('id'), view,
                                                                        Entity.View))
                if view_js.get('count') == 0:
                    raise InvalidParam(
                        'View named {} was not found in configuration {}'.format(view, configuration))
                ancestor += ' and ' + 'ancestor.id:{}'.format(view_js.get('data')[0].get('id'))
                if collection == Collections.ZONES:
                    collection_rs = rest_v2.get_zone_by_name(collection_name)
                else:
                    collection_name = collection_name.split('.')[0]
                    collection_rs = rest_v2.get_v2(
                        "{} and name:'{}' and type:'{}'".format(ancestor, collection_name, collection_type))
            elif collection == Collections.NETWORKS:
                collection_rs = rest_v2.get_network_by_range(collection_name, ancestor)
            elif collection == Collections.BLOCKS:
                collection_rs = rest_v2.get_block_by_range(collection_name, ancestor)

            if collection_rs.get('count') == 0:
                raise InvalidParam(
                    'Not found collection: {} with collection named: {} in configuration {}'.format(collection,
                                                                                                    collection_name,
                                                                                                    configuration))
            cls_data = collection_rs.get('data')[0]
            filter_server = data.get('server')
            filter_string = ''
            if filter_server:
                server = rest_v2.get_server_by_name_in_configuration(configuration_id=configuration_js.get('id'),
                                                                     server_name=filter_server).get('data')[0]
                server_scope_filters = ['null', "{}".format(server.get('id'))]
                if server.get('serverGroup') is not None:
                    server_scope_filters.append("{}".format(server.get('serverGroup', {}).get('id')))
                filter_string = 'serverScope.id:in({})'.format(','.join(server_scope_filters))

            deployment_options = rest_v2.get_deployment_option_by_collection(
                EntityV2.get_collection(cls_data.get('type')), cls_data.get('id'), filter_string,
                'id,name,type,range,value,definition,code,userDefinedFields,serverScope,_inheritedFrom'
            )
            for option in deployment_options.get('data'):
                inherited_from = option.get('_inheritedFrom')
                if inherited_from:
                    inherited_href = common.get_links_href(inherited_from.get('_links'))
                    if inherited_href:
                        fields = 'id,name,type' if collection in ZoneTypeCls.FORWARDER_ZONE else 'id,name,type,range'
                        if inherited_from.get('type') == EntityV2.ZONE:
                            fields += ',absoluteName'
                        inherited_cls = rest_v2.link_api(inherited_href, fields=fields)
                        option['_inheritedFrom'] = inherited_cls
                try:
                    definition_href = common.get_links_href(option.get('definition').get('_links'))
                    display_name = rest_v2.link_api(definition_href, fields='displayName').get('displayName')
                    option['displayName'] = display_name
                except Exception as e:
                    g.user.logger.warning(
                        'Failed to get display name of DNS Option {}: {}'.format(option.get('name'), str(e)))

            return make_response(jsonify(deployment_options))
        except BAMV2ErrorResponse as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(e.response.json(), e.status)
        except UnexpectedResponse as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(e.response.json(), e.response.status)
        except UserException as e:
            if isinstance(e, BAMAuthException):
                return make_response(jsonify(str(e)), 401)
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 403)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)

    @rest_v2_handler
    @util.no_cache
    @deployment_option_ns.expect(deployment_option_parsers.create_deployment_option_parser)
    def post(self, configuration):
        """ Create deployment options for a resource.
        """
        try:
            data = deployment_option_parsers.create_deployment_option_parser.parse_args()
            collection = data.get('collection')
            collection_name = data.get('collection_name')
            if not collection_name:
                raise InvalidParam('Missing collection.')
            # TODO: need to define model for options
            options = data.get('options')[0]
            rest_v2 = g.user.v2
            configuration_js = rest_v2.get_configuration_by_name(configuration).get('data')[0]
            collection_type = Collections.get_entity_type(collection)
            ancestor = 'ancestor.id:{}'.format(configuration_js.get('id'))

            collection_rs = {
                "count": 0
            }
            if collection in ZoneTypeCls.FORWARDER_ZONE:
                view = data.get('view')
                if not view:
                    raise InvalidParam('Missing view.')

                view_js = rest_v2.get_v2(
                    "ancestor.id:{} and name:'{}' and type:'{}'".format(configuration_js.get('id'), view, Entity.View))
                if view_js.get('count') == 0:
                    raise InvalidParam(
                        'View named {} was not found in configuration {}'.format(view, configuration))
                ancestor += ' and ' + 'ancestor.id:{}'.format(view_js.get('data')[0].get('id'))

                collection_name = collection_name.split('.')[0]
                collection_rs = rest_v2.get_v2(
                    "{} and name:'{}' and type:'{}'".format(ancestor, collection_name, collection_type))
            elif collection == Collections.NETWORKS:
                collection_rs = rest_v2.get_network_by_range(collection_name, ancestor)
            elif collection == Collections.BLOCKS:
                collection_rs = rest_v2.get_block_by_range(collection_name, ancestor)

            if collection_rs.get('count') == 0:
                raise InvalidParam(
                    'Not found collection: {} with collection named: {} in configuration {}'.format(collection,
                                                                                                    collection_name,
                                                                                                    configuration))
            cls_data = collection_rs.get('data')[0]
            deployment_options = []
            for option in options:
                deployment_options.append(rest_v2.add_deployment_option(collection, cls_data.get('id'), option))
            return make_response(jsonify({"count": len(deployment_options), "data": deployment_options}))
        except BAMV2ErrorResponse as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(e.response.json(), e.status)
        except UnexpectedResponse as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(e.response.json(), e.response.status)
        except UserException as e:
            if isinstance(e, BAMAuthException):
                return make_response(jsonify(str(e)), 401)
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e), 403))
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


@util.exception_catcher
@require_permission('rest_page')
@deployment_option_ns.route('/deployment_options')
class RemoveDeploymentOption(Resource):
    @rest_v2_handler
    @util.no_cache
    @deployment_option_ns.expect(deployment_option_models.delete_deployment_option_model)
    def delete(self, ):
        """ Delete deployment options by id.
        """
        try:
            data = deployment_option_parsers.delete_deployment_option_parser.parse_args()
            ids = data.get('ids')
            rest_v2 = g.user.v2
            for option_id in ids:
                rest_v2.delete_deployment_option(option_id)
            return make_response(jsonify(""), 204)
        except BAMV2ErrorResponse as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(e.response.json(), e.status)
        except UnexpectedResponse as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(e.response.json(), e.response.status)
        except UserException as e:
            if isinstance(e, BAMAuthException):
                return make_response(jsonify(str(e)), 401)
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e), 403))
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)
