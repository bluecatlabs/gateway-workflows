# Copyright 2022 BlueCat Networks (USA) Inc. and its affiliates. All Rights Reserved.
import os
import sys
import configparser
import traceback

from flask_restplus import Resource

from flask import render_template, g, jsonify, make_response

from app_user import UserSession
from bluecat import route, util
from bluecat.util.util import encrypt_key
import config.default_config as config

from main_app import app, api

from .common.constant import UserType, CONFIG, CONFIG_PATH_FOR_CREDENTIAL, DefaultConfiguration
from .libs.model.encrypt_credential_model import encrypt_credential_model
from .libs.parse.encrypt_credential_parser import encrypt_credential_parser

# DO NOT REMOVE import below
from . import tag_groups, mac_address, search


def module_path():
    encoding = sys.getfilesystemencoding()
    return os.path.dirname(os.path.abspath(__file__))


@route(app, '/device_registration/device_registration_endpoint')
@util.workflow_permission_required('device_registration_page')
@util.exception_catcher
@util.ui_secure_endpoint
def device_registration_device_registration_page():
    return render_template(
        'device_registration_page.html',
        text=util.get_text(module_path(), config.language),
        options=g.user.get_options(),
    )


@api.route('/configuration_name/')
class ConfigurationFile(Resource):
    @util.rest_workflow_permission_required('device_registration_page')
    @util.no_cache
    def get(self):
        """  """
        try:
            import config.default_config as config
            config_name = config.default_configuration if config.default_configuration else DefaultConfiguration.CONFIG_NAME
            return jsonify(config_name)
        except Exception as ex:
            g.user.logger.info(str(ex))
            return "Please set default configuration in Administration > Configuration > General Configuration", 500


@api.route('/encrypt/credential/')
class Credential(Resource):
    @util.rest_workflow_permission_required('device_registration_page')
    @util.no_cache
    @api.expect(encrypt_credential_model, validate=True)
    def post(self):
        try:
            data = encrypt_credential_parser.parse_args()
            username = data.get(UserType.USERNAME, '')
            password = data.get(UserType.PASSWORD, '')
            bam_api = g.user.get_api_netloc(True)
            user = UserSession.validate(bam_api, username, password)
            if user:
                if user.get_user_type() == UserType.ADMIN:
                    encrypted_password = encrypt_key(password.encode()).decode()
                    config = configparser.ConfigParser()
                    config.read(CONFIG_PATH_FOR_CREDENTIAL)
                    config[CONFIG.BAM_CONFIG][CONFIG.ADMIN_USERNAME] = username
                    config[CONFIG.BAM_CONFIG][CONFIG.ADMIN_PASSWORD] = encrypted_password
                    return make_response(encrypted_password)
                else:
                    return make_response(jsonify("This user is not an admin"), 400)
            else:
                return make_response(jsonify("Invalid username and password"), 400)
        except Exception as e:
            g.user.logger.error(traceback.format_exc())
            return make_response(jsonify(str(e)), 500)