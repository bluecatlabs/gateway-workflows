# Copyright 2022 BlueCat Networks (USA) Inc. and its affiliates. All Rights Reserved.
import traceback

from flask import g, jsonify, make_response
from flask_restplus import Resource

from bluecat import util
from main_app import api
from .common.common import get_tags_from_tag_group, get_locations_and_dns_and_networks, read_config_file

tags_ns = api.namespace('tags', description='Tag operation')
TAG_GROUP_NAME = read_config_file('BAM_CONFIG', 'TAG_GROUP')


@tags_ns.route('/')
class Tag(Resource):

    @util.rest_workflow_permission_required('device_registration_page')
    @util.no_cache
    def get(self):
        try:
            result = []
            tags = get_tags_from_tag_group(TAG_GROUP_NAME)
            for tag in tags:
                result.append({
                    tag.get_name(): ""
                })
            return jsonify(result)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)


@tags_ns.route('/<string:tag_name>/locations/')
class Location(Resource):

    @util.rest_workflow_permission_required('device_registration_page')
    @util.no_cache
    def get(self, tag_name):
        try:
            tags = get_tags_from_tag_group(TAG_GROUP_NAME)
            tags_name = [tag.get_name() for tag in tags if tag_name == tag.get_name()]
            if not tags_name:
                return jsonify("Tag {} not found in tag group {}".format(tag_name, TAG_GROUP_NAME))
            return jsonify(get_locations_and_dns_and_networks(TAG_GROUP_NAME, tag_name))
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)
